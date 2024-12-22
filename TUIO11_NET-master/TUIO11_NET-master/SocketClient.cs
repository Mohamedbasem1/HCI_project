using System;
using System.Net.Sockets;
using System.Text;

public class SocketClient
{
    private string serverIP = "127.0.0.1"; // IP address of the Python server
    private int port = 5000;               // Port number matching the Python server

    public void SendMarkerData(string markerData)
    {
        try
        {
            // Create a TCP/IP socket
            TcpClient client = new TcpClient(serverIP, port);

            // Convert the marker data to byte array
            byte[] data = Encoding.UTF8.GetBytes(markerData);

            // Get the stream to send data
            NetworkStream stream = client.GetStream();

            // Send the marker data to the server
            stream.Write(data, 0, data.Length);
            Console.WriteLine("Sent: {0}", markerData);

            // Receive the response from the Python server
            byte[] buffer = new byte[1024];
            int bytesRead = stream.Read(buffer, 0, buffer.Length);
            string responseData = Encoding.UTF8.GetString(buffer, 0, bytesRead);
            Console.WriteLine("Received: {0}", responseData);

            // Close everything
            stream.Close();
            client.Close();
        }
        catch (Exception e)
        {
            Console.WriteLine("Exception: {0}", e);
        }
    }
}
