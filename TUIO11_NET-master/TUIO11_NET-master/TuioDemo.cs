/*
	TUIO C# Demo - part of the reacTIVision project
	Copyright (c) 2005-2016 Martin Kaltenbrunner <martin@tuio.org>

	This program is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation; either version 2 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, write to the Free Software
	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/

using System;
using System.Drawing;
using System.Windows.Forms;
using System.ComponentModel;
using System.Collections.Generic;
using System.Collections;
using System.Threading;
using TUIO;
using System.IO;
using System.Drawing.Drawing2D;
using System.Net.Sockets;
using System.Text;
using System.Net.Http;  // For HttpClient and StringContent
using Newtonsoft.Json;  // For JsonConvert
using System.Timers;
using static System.Windows.Forms.VisualStyles.VisualStyleElement.TaskbarClock;




public class TuioDemo : Form, TuioListener
{
    private TuioClient client;
    private Dictionary<long, TuioObject> objectList;
    private Dictionary<long, TuioCursor> cursorList;
    private Dictionary<long, TuioBlob> blobList;

    public static int width, height;
    private int window_width = 640;
    private int window_height = 480;
    private int window_left = 0;
    private int window_top = 0;
    private int screen_width = Screen.PrimaryScreen.Bounds.Width;
    private int screen_height = Screen.PrimaryScreen.Bounds.Height;
    public int prev_id = -1;
    public int selected_id = 1;


    private bool fullscreen;
    private bool firstopen = true;
    private bool verbose;
    private bool displayStretchPage = false;
    private float leftMarkerX = 0, leftMarkerY = 0;
    private float rightMarkerX = 0, rightMarkerY = 0;
    private bool isGoodStretch = false;
    private int stretchCount = 0;
    // public bool patientList = false;
    private System.Timers.Timer idTimer;
    private bool isIdVisible = false;
    private const int targetId = 12;// Target ID to track
    private const double requiredTime = 5000; // 5 seconds in milliseconds
    private Dictionary<long, DateTime> objectDetectionTimes = new Dictionary<long, DateTime>();
    private const double detectionThreshold = 5000; // 5 seconds

    public string serverIP = "DESKTOP-8161GCK"; // IP address of the Python server
    public int port = 8000;               // Port number matching the Python server
    int flag = 0;
    Font font = new Font("Arial", 10.0f);
    SolidBrush fntBrush = new SolidBrush(Color.White);
    SolidBrush bgrBrush = new SolidBrush(Color.FromArgb(0, 0, 64));
    SolidBrush curBrush = new SolidBrush(Color.FromArgb(192, 0, 192));
    SolidBrush objBrush = new SolidBrush(Color.FromArgb(64, 0, 0));
    SolidBrush blbBrush = new SolidBrush(Color.FromArgb(64, 64, 64));
    Pen curPen = new Pen(new SolidBrush(Color.Blue), 1);
    private string objectImagePath;
    private string backgroundImagePath;
    TcpClient client1;
    NetworkStream stream;
    public TuioDemo(int port)
    {
        idTimer = new System.Timers.Timer(requiredTime);
        idTimer.AutoReset = false;
        idTimer.Elapsed += OnIdTimerElapsed;

        verbose = false;
        fullscreen = true;
        width = screen_width;
        height = screen_height;

        window_left = this.Left;
        window_top = this.Top;

        this.FormBorderStyle = FormBorderStyle.None;
        this.Left = 0;
        this.Top = 0;
        this.Width = screen_width;
        this.Height = screen_height;

        this.ClientSize = new System.Drawing.Size(width, height);
        this.Name = "TuioDemo";
        this.Text = "TuioDemo";

        this.Closing += new CancelEventHandler(Form_Closing);
        this.KeyDown += new KeyEventHandler(Form_KeyDown);

        this.SetStyle(ControlStyles.AllPaintingInWmPaint |
                        ControlStyles.UserPaint |
                        ControlStyles.DoubleBuffer, true);
        objectList = new Dictionary<long, TuioObject>(128);
        cursorList = new Dictionary<long, TuioCursor>(128);
        blobList = new Dictionary<long, TuioBlob>(128);
        readpatient();
        DrawPatientTable(); // Populate the cached bitmap with the table

        client = new TuioClient(port);
        client.addTuioListener(this);

        client.connect();

        // Create a TCP/IP socket
        client1 = new TcpClient("localhost", 65434);
        // Get the stream to send data
        stream = client1.GetStream();

    }
    private void OnIdTimerElapsed(object sender, ElapsedEventArgs e)
    {
        // The ID has been visible for 5 seconds, trigger click event
        SendClickMessage();
        idTimer.Stop();
    }

    private void Form_KeyDown(object sender, System.Windows.Forms.KeyEventArgs e)
    {

        if (e.KeyData == Keys.F1)
        {
            if (fullscreen == false)
            {

                width = screen_width;
                height = screen_height;

                window_left = this.Left;
                window_top = this.Top;

                this.FormBorderStyle = FormBorderStyle.None;
                this.Left = 0;
                this.Top = 0;
                this.Width = screen_width;
                this.Height = screen_height;

                fullscreen = true;
            }
            else
            {

                width = window_width;
                height = window_height;

                this.FormBorderStyle = FormBorderStyle.Sizable;
                this.Left = window_left;
                this.Top = window_top;
                this.Width = window_width;
                this.Height = window_height;

                fullscreen = false;
            }
        }
        else if (e.KeyData == Keys.Escape)
        {
            // Close everything
            stream.Close();
            client1.Close();
            this.Close();

        }
        else if (e.KeyData == Keys.V)
        {
            verbose = !verbose;
        }

    }
    public class patient
    {
        public string name, id, inj, exer;
    }
    List<patient> patients = new List<patient>();
    void readpatient()
    {
       
    }
    private void Form_Closing(object sender, System.ComponentModel.CancelEventArgs e)
    {

        client.removeTuioListener(this);

        client.disconnect();
        System.Environment.Exit(0);
    }

    public void addTuioObject(TuioObject o)
    {
        if (o.SymbolID == targetId)
        {
            if (!isIdVisible)
            {
                isIdVisible = true;
                idTimer.Start(); // Start the timer when the target ID appears
            }
        }
        if (o.SymbolID >= 50)
        {
            // Track the time when the object with ID 50 is first detected
            if (!objectDetectionTimes.ContainsKey(o.SessionID))
            {
                objectDetectionTimes[o.SessionID] = DateTime.Now;
            }
        }
        lock (objectList)
        {
            objectList.Add(o.SessionID, o);
        }
        if (verbose) Console.WriteLine("add obj " + o.SymbolID + " (" + o.SessionID + ") " + o.X + " " + o.Y + " " + o.Angle);
    }

    public void updateTuioObject(TuioObject o)
    {
        if (verbose) Console.WriteLine("set obj " + o.SymbolID + " " + o.SessionID + " " + o.X + " " + o.Y + " " + o.Angle + " " + o.MotionSpeed + " " + o.RotationSpeed + " " + o.MotionAccel + " " + o.RotationAccel);
        if (o.SymbolID >= 50)
        {
            // Check if the object with ID 50 has been visible for 5 seconds
            if (objectDetectionTimes.ContainsKey(o.SessionID))
            {
                DateTime detectionTime = objectDetectionTimes[o.SessionID];
                TimeSpan elapsed = DateTime.Now - detectionTime;

                if (elapsed.TotalMilliseconds >= detectionThreshold)
                {
                    // Send data after 5 seconds of detection
                    SendMarkerIdAsync(o.SymbolID); // You can send additional data if needed
                    objectDetectionTimes.Remove(o.SessionID); // Remove after sending
                }
            }
        }

        if (o.SymbolID == 10)
        {  // Directly handle rotation ID
            UpdateSelectedIdBasedOnRotation(o);
        }
        if (o.SymbolID == 22) // Left marker
        {
            leftMarkerX = o.getX() * width;
            leftMarkerY = o.getY() * height;
        }
        else if (o.SymbolID == 23) // Right marker
        {
            rightMarkerX = o.getX() * width;
            rightMarkerY = o.getY() * height;
        }
        else if (o.SymbolID == 2) // Clear page and reset stretch
        {
            displayStretchPage = true;
            stretchCount = 0; // reset counter if needed
            Invalidate(); // Redraw the screen to clear it
        }

        if (displayStretchPage)
        {
            float distance = (float)Math.Sqrt((rightMarkerX - leftMarkerX) * (rightMarkerX - leftMarkerX) + (rightMarkerY - leftMarkerY) * (rightMarkerY - leftMarkerY));
            bool previousStretch = isGoodStretch;
            isGoodStretch = distance > 300; // Threshold for a good stretch

            if (isGoodStretch && !previousStretch)
            {
                stretchCount++;
            }

            Invalidate(); // Refresh the form to update UI with new information
        }
        if (o.SymbolID == targetId && !isIdVisible)
        {
            isIdVisible = true;
            idTimer.Start(); // Start or reset the timer when the target ID updates
        }
    }



    public void removeTuioObject(TuioObject o)
    {
        lock (objectList)
        {
            objectList.Remove(o.SessionID);
        }
        if (verbose) Console.WriteLine("del obj " + o.SymbolID + " (" + o.SessionID + ")");
        if (o.SymbolID >= 50 && objectDetectionTimes.ContainsKey(o.SessionID))
        {
            // Remove detection time if the object with ID 50 is removed
            objectDetectionTimes.Remove(o.SessionID);
        }
        if (o.SymbolID == targetId)
        {
            isIdVisible = false;
            idTimer.Stop(); // Stop the timer if the target ID disappears
        }
    }


    public void addTuioCursor(TuioCursor c)
    {
        lock (cursorList)
        {
            cursorList.Add(c.SessionID, c);
        }
        if (verbose) Console.WriteLine("add cur " + c.CursorID + " (" + c.SessionID + ") " + c.X + " " + c.Y);
    }

    public void updateTuioCursor(TuioCursor c)
    {
        if (verbose) Console.WriteLine("set cur " + c.CursorID + " (" + c.SessionID + ") " + c.X + " " + c.Y + " " + c.MotionSpeed + " " + c.MotionAccel);
    }

    public void removeTuioCursor(TuioCursor c)
    {
        lock (cursorList)
        {
            cursorList.Remove(c.SessionID);
        }
        if (verbose) Console.WriteLine("del cur " + c.CursorID + " (" + c.SessionID + ")");
    }

    public void addTuioBlob(TuioBlob b)
    {
        lock (blobList)
        {
            blobList.Add(b.SessionID, b);
        }
        if (verbose) Console.WriteLine("add blb " + b.BlobID + " (" + b.SessionID + ") " + b.X + " " + b.Y + " " + b.Angle + " " + b.Width + " " + b.Height + " " + b.Area);
    }

    public void updateTuioBlob(TuioBlob b)
    {

        if (verbose) Console.WriteLine("set blb " + b.BlobID + " (" + b.SessionID + ") " + b.X + " " + b.Y + " " + b.Angle + " " + b.Width + " " + b.Height + " " + b.Area + " " + b.MotionSpeed + " " + b.RotationSpeed + " " + b.MotionAccel + " " + b.RotationAccel);
    }

    public void removeTuioBlob(TuioBlob b)
    {
        lock (blobList)
        {
            blobList.Remove(b.SessionID);
        }
        if (verbose) Console.WriteLine("del blb " + b.BlobID + " (" + b.SessionID + ")");
    }

    public void refresh(TuioTime frameTime)
    {
        Invalidate();
    }

    // Declare the flag and cached bitmap
    public bool patientList = false;
    public Bitmap tableBitmap = null;

    public void DrawPatientTable()
    {
        // Define the size of the table
        int tableWidth = 600;
        int tableHeight = 400;

        // Create the bitmap for caching the table
        tableBitmap = new Bitmap(tableWidth, tableHeight);
        using (Graphics g = Graphics.FromImage(tableBitmap))
        {
            Font headerFont = new Font("Arial", 14, FontStyle.Bold);
            Font tableFont = new Font("Arial", 12);
            Brush tableBrush = Brushes.White;
            Brush headerBrush = Brushes.Yellow;

            float x = 0;
            float y = 0;
            float rowHeight = 30f;
            float colWidth = 150f;
            float padding = 10f;
            Pen pen = new Pen(Color.Black, 2);

            string[] headers = { "ID", "Name", "Injury", "Exercise" };
            for (int j = 0; j < headers.Length; j++)
            {
                g.DrawString(headers[j], headerFont, headerBrush, new PointF(x + (j * colWidth) + padding, y + padding));
            }

            g.DrawLine(pen, x, y + rowHeight, x + (colWidth * headers.Length), y + rowHeight);
            for (int i = 0; i < patients.Count; i++)
            {
                patient p = patients[i];
                string[] patientInfo = { p.id, p.name, p.inj, p.exer };
                for (int j = 0; j < patientInfo.Length; j++)
                {
                    g.DrawString(patientInfo[j], tableFont, tableBrush, new PointF(x + (j * colWidth) + padding, y + ((i + 1) * rowHeight) + padding));
                }
                g.DrawLine(pen, x, y + ((i + 2) * rowHeight), x + (colWidth * headers.Length), y + ((i + 2) * rowHeight)); // Horizontal border
            }

            for (int j = 0; j <= headers.Length; j++)
            {
                g.DrawLine(pen, x + (j * colWidth), y, x + (j * colWidth), y + (rowHeight * (patients.Count + 1))); // Vertical border
            }

            pen.Dispose();
        }
    }

    protected override void OnPaintBackground(PaintEventArgs pevent)
    {
        // Getting the graphics object
        Graphics g = pevent.Graphics;
        g.FillRectangle(bgrBrush, new Rectangle(0, 0, width, height));

        if (displayStretchPage)
        {
            string stretchStatus = isGoodStretch ? "Good Stretch! Count: " + stretchCount : "Keep Stretching...";
            g.DrawString(stretchStatus, font, fntBrush, new PointF(10, 40)); // Display stretching status
        }
        string[,] exercisesTable = {
                                {"ID", "Name", "Leg Injuries", "Exercise"},
                                {"1", "John Doe", "Knee Sprain", "Quad Stretch"},
                                {"2", "Jane Smith", "Hamstring Strain", "Hamstring Curl"},
                                {"3", "Tom Lee", "Ankle Sprain", "Calf Raises"},
                                {"4", "Anna Brown", "IT Band Syndrome", "Side-Lying Leg Lifts"},
                                {"5", "Michael Clark", "Shin Splints", "Toe Taps"},
                                {"6", "Emily Davis", "Achilles Tendonitis", "Eccentric Heel Drops"},
                                {"7", "David Harris", "Quadriceps Strain", "Straight Leg Raise"},
                                {"8", "Sophia Miller", "Groin Strain", "Hip Adductor Stretch"},
                                {"9", "James Wilson", "Calf Strain", "Seated Calf Stretch"},
                                {"10", "Olivia Moore", "Hip Flexor Strain", "Hip Flexor Stretch"},
                                {"11", "Liam Martinez", "Patellar Tendonitis", "Wall Squats"},
                                {"12", "Mia Rodriguez", "Piriformis Syndrome", "Piriformis Stretch"},
                            };
        if (patientList && tableBitmap != null)
        {
            g.DrawImage(tableBitmap, new Point(50, 100)); // Make sure tableBitmap is drawn here
        }

        // Draw other TUIO objects
        if (objectList.Count > 0)
        {
            lock (objectList)
            {
                foreach (TuioObject tobj in objectList.Values)
                {
                    int ox = tobj.getScreenX(width);
                    int oy = tobj.getScreenY(height);
                    int size = height / 10;

                    // Draw the object rectangle
                    g.FillRectangle(objBrush, new Rectangle(ox - size / 2, oy - size / 2, size, size));
                    g.DrawString(tobj.SymbolID.ToString(), font, fntBrush, new PointF(ox - 10, oy - 10));
                    g.DrawString("Selected ID", font, fntBrush, new PointF(this.Width - 100, 80));
                    g.DrawString(selected_id.ToString(), font, fntBrush, new PointF(this.Width - 100, 100));

                    // Handling the drawing and logic for specific Symbol IDs
                    switch (tobj.SymbolID)
                    {
                        case 0:
                            patientList = true;
                            float y = 0; // Starting y position for the table
                            float rowHeight = 30f;
                            float padding = 10f;
                            float colWidth = 150f; // Width of each column

                            Font tableFont = new Font("Arial", 12);
                            Brush tableBrush = Brushes.Black;
                            UpdateSelectedIdBasedOnRotation(tobj);
                            for (int i = 0; i < patients.Count; i++)
                            {
                                patient p = patients[i];
                                int currentPatientId = int.Parse(p.id);

                                if (currentPatientId == selected_id)
                                {
                                    g.FillRectangle(Brushes.Red, new RectangleF(50, 100 + (i + 1) * rowHeight, 600, rowHeight));
                                    string[] patientInfo = { p.id, p.name, p.inj, p.exer };
                                    for (int j = 0; j < patientInfo.Length; j++)
                                        g.DrawString(patientInfo[j], tableFont, tableBrush, new PointF(50 + (j * colWidth) + padding, 100 + ((i + 1) * rowHeight) + padding));
                                }
                            }
                            break;

                        case 5:
                            // Hide the table when another SymbolID appears
                            patientList = false;
                            string rowData = $"Selected ID: {exercisesTable[selected_id, 0]}, " +
                                             $"Name: {exercisesTable[selected_id, 1]}, " +
                                             $"Leg Injury: {exercisesTable[selected_id, 2]}, " +
                                             $"Exercise: {exercisesTable[selected_id, 3]}";
                            SendMarkerData("the selected patient :" + rowData);
                            break;

                        case 2:
                            // Additional handling for SymbolID 2, if necessary
                            patientList = false;
                            break;
                    }
                }
            }
        }
    }

    private float previousAngle = 0;
    private float smoothingFactor = 5.0f; // Adjust this value to change sensitivity
    private float minAngleDifference = 5.0f; // Minimum angle to consider a rotation
    private DateTime lastRotationTime = DateTime.Now; // Last time the rotation was updated

    private void UpdateSelectedIdBasedOnRotation(TuioObject tobj)
    {
        float currentAngle = tobj.Angle * (180 / (float)Math.PI);  // Convert radians to degrees
        currentAngle = NormalizeAngle(currentAngle);
        float angleDifference = currentAngle - previousAngle;
        // Check if the marker ID is greater than 50 and send it to the socket

        // Ensure that the difference is greater than the smoothing factor
        if (Math.Abs(angleDifference) > minAngleDifference)
        {
            // Introduce a cooldown period for rotation changes
            if ((DateTime.Now - lastRotationTime).TotalMilliseconds > 200) // 200ms cooldown
            {
                if (angleDifference > 0)
                {
                    selected_id = (selected_id + 1) % 13;  // Adjust for 12 patients
                    SendRotationEventAsync("rotate_right");
                }
                else
                {
                    selected_id = (selected_id - 1 + 13) % 13;  // Wrap around if negative
                    SendRotationEventAsync("rotate_left");
                }

                // Invalidate to trigger redraw
                this.Invalidate();
                lastRotationTime = DateTime.Now; // Update last rotation time
            }
        }

        previousAngle = currentAngle;  // Update previous angle
    }


    public async void SendRotationEventAsync(string rotationDirection)
    {
        try
        {
            string message = rotationDirection + "\n";
            byte[] data = Encoding.UTF8.GetBytes(message);

            await stream.WriteAsync(data, 0, data.Length);
            Console.WriteLine($"Sent rotation event: {rotationDirection}");
            await stream.FlushAsync(); // Flush to ensure data is sent immediately
        }
        catch (Exception e)
        {
            Console.WriteLine("Socket error: " + e.Message);
        }
    }
    private async void SendClickMessage()
    {
        try
        {
            string message = "click\n";  // Define the message content for a click event
            byte[] data = Encoding.UTF8.GetBytes(message);

            await stream.WriteAsync(data, 0, data.Length);
            Console.WriteLine("Sent click event due to ID 11 detected for 5 seconds");
            await stream.FlushAsync();  // Ensure the message is sent immediately
        }
        catch (Exception e)
        {
            Console.WriteLine("Error sending click message: " + e.Message);
        }
    }



    private float NormalizeAngle(float angle)
    {
        while (angle < 0) angle += 360;
        while (angle >= 360) angle -= 360;
        return angle;
    }
    public async void SendMarkerIdAsync(int markerId)
    {
        try
        {
            string message = $"marker_id:{markerId}\n";
            byte[] data = Encoding.UTF8.GetBytes(message);

            await stream.WriteAsync(data, 0, data.Length);
            Console.WriteLine($"Sent marker ID: {markerId}");
            await stream.FlushAsync(); // Flush to ensure data is sent immediately
        }
        catch (Exception e)
        {
            Console.WriteLine("Socket error: " + e.Message);
        }
    }

    public static void Main(String[] argv)
    {
        int port = 0;
        switch (argv.Length)
        {
            case 1:
                port = int.Parse(argv[0], null);
                if (port == 0) goto default;
                break;
            case 0:
                port = 3333;
                break;
            default:
                Console.WriteLine("usage: mono TuioDemo [port]");
                System.Environment.Exit(0);
                break;
        }

        TuioDemo app = new TuioDemo(port);
        Application.Run(app);
    }
    public void SendMarkerData(string s)
    {

        try
        {
            // Replace with your TUIO marker data
            // string markerData1 = $"Marker ID: {markerData.SymbolID.ToString()}, X: {markerData.X.ToString()}, Y: {markerData.Y.ToString()}";
            // string markerData1 = $"Selected ID :P{s}";

            // Convert the marker data to byte array
            byte[] data = Encoding.UTF8.GetBytes(s);


            // Send the marker data to the server
            stream.Write(data, 0, data.Length);
            Console.WriteLine("Sent: {0}", s);


        }
        catch (Exception e)
        {
        }
    }
}