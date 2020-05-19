// File Name GreetingServer.java
import java.net.*;
import java.io.*;
import java.util.Date;

public class server extends Thread {
	private ServerSocket serverSocket;
	
	public server(int port) throws IOException {
		serverSocket = new ServerSocket(port);
		serverSocket.setSoTimeout(10000);
	}

	public void run() {
		while(true) {
			try {
				Date today = new Date();
				String httpResponse = "HTTP/1.0 404 Not Found\r\n"+
									"Content-type: text/html\r\n\r\n"+
									"<html><head><p>Welcome to Transperth</p></head><body>";
				
				System.out.println("Waiting for client on port " + 
					serverSocket.getLocalPort() + "...");
				Socket server = serverSocket.accept();
				
				System.out.println("Just connected to " + server.getRemoteSocketAddress());
				DataInputStream in = new DataInputStream(server.getInputStream());
				
				System.out.println(in.readUTF());
				DataOutputStream out = new DataOutputStream(server.getOutputStream().write(httpResponse.getBytes("UTF-8")));
				server.close();
				
			} catch (SocketTimeoutException s) {
				System.out.println("Socket timed out!");
				break;
			} catch (IOException e) {
				e.printStackTrace();
				break;
			}
		}
	}
	
	public static void main(String [] args) {
		int port = Integer.parseInt(args[0]);
		try {
			Thread t = new server(port);
			t.start();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}