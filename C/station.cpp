// g++ station.cpp -o station
// ./station East_Station 4003 4004 4002 4008 4006

#include <unistd.h>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <string.h>
#include <iostream>
#include <vector>
#include <typeinfo>
#include <iterator>

#define host "localhost"

using namespace std;

void print(vector<int> const &input){
    copy(input.begin(),input.end(), ostream_iterator<int>(cout, " "));
}


int main(int argc, char const *argv[]){
    
    string staion_name = argv[1];
    int TCP_port = stoi(argv[2]);
    int UDP_port = stoi(argv[3]);
    vector<int> Neighbour;
    for(int i=4; i<argc; i++){
        Neighbour.push_back(stoi(argv[i] ));
    }
    // for(int i=0; i<Neighbour.size(); i++){
    //     cout << "Neighb are" << Neighbour.at(i) <<"\n";
    // }

    int server_fd, new_socket, valread;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);
    char buffer[1024] = {0};
    char message[] = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=ISO-8859-4 \r\n\r\n<h1>This is the msg from the server</h1>";

    // Create socket fd
    if(( server_fd = socket(AF_INET, SOCK_STREAM,0)) == 0 ){
        perror(" socket failed ");
        exit(EXIT_FAILURE);
    }

    // Attaching socket to the TCP port
    if(setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt))){
        perror("setssockopt");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr  = INADDR_ANY;
    address.sin_port = htons(TCP_port);

    // Attaching socket to the TCP
    if(bind(server_fd, (struct sockaddr *)&address, sizeof(address))<0 ){
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    if(listen(server_fd, 3) < 0){
        perror("Listen");
        exit(EXIT_FAILURE);
    }

    if((new_socket= accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen))<0){
        perror("accept");
        exit(EXIT_FAILURE);
    }

    valread = read(new_socket, buffer, 1024);
    send(new_socket, message, strlen(message), 0);
    return 0;

}