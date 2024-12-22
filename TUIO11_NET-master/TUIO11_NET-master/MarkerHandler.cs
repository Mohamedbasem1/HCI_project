public class MarkerHandler
{
    public void HandleMarker(TuioMarker marker)
    {
        // Create the marker data string
        string markerData = $"Marker ID: {marker.Id}, X: {marker.X}, Y: {marker.Y}";

        // Send marker data to the Python server
        SocketClient socketClient = new SocketClient();
        socketClient.SendMarkerData(markerData);
    }
}
