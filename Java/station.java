import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Date;


public class station {

	public static void main(String args[]) throws IOException {

		ServerSocket server = new ServerSocket(4003);
		int portNum = serverSocket.getLocalPort()
		System.out.println("Listening for connection ...." + portNum.toString());
		
		while (true) {
			try{
				// accept connection
				Socket socket = server.accept()) 
				Date today = new Date();
				String httpResponse = "HTTP/1.1 200 OK\r\n\r\n" + today;
				socket.getOutputStream().write(httpResponse.getBytes("UTF-8"));
			}
		}
	}
}
