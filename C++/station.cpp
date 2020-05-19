// ./station East_Station 4003 4004 4002 4008 4006

/*
    Nicholas Walters
    22243339

Sources/Acknowledgements:
    basic implementation of select()
    https://www.geeksforgeeks.org/tcp-and-udp-server-using-select/
    
*/



// Server program 
#include <arpa/inet.h> 
#include <errno.h> 
#include <netinet/in.h> 
#include <signal.h> 
#include <stdio.h> 
#include <stdlib.h> 
#include <strings.h> 
#include <sys/socket.h> 
#include <sys/types.h> 
#include <unistd.h>
#include <string.h>
#include <sys/select.h>
#include <time.h>

#include <typeinfo>
#include <iterator>
#include <string>
#include <iostream>
#include <fstream>
#include <vector>
#include <ctime>
#include <iostream>


using namespace std;


#define MAXLINE 1024
#define MAXSTATIONS 100
#define MAX_ROUTES 1000


string routes[MAX_ROUTES];
vector<string> neighbourNames;
vector<string> routeList;
vector<string> final;
bool direct = false;



int max(int x, int y) 
{ 
    if (x > y) 
        return x; 
    else
        return y; 
} 


char *getURI(char *header){
    char *token;
    token = strtok(header, " ");
    int i=-1;
    while (token != NULL)
    {
        i++;
        token = strtok (NULL, " ");
        if(i == 0){
            printf("the URI is: \n");
            printf ("%s\n", token);
            printf("\n\n");
            return token;
        }
    }
    return NULL; 
}


void printS(vector<string> const &input){
    copy(input.begin(),input.end(), ostream_iterator<string>(cout, " "));
}


bool isDirect(string stnName){    
    for(int i=0; i<routeList.size(); ++i){
        string line;
        line = routeList.at(i);
        reverse(line.begin(), line.end());
        string station = line.substr(0, line.find(","));
        reverse(station.begin(), station.end());
        
        if(strcmp(stnName.c_str(), station.c_str()) == 0){
            return true;
        }
    }
    return false;
}




const string currentDateTime() {
    time_t     now = time(0);
    struct tm  tstruct;
    char       buf[80];
    tstruct = *localtime(&now);
    strftime(buf, sizeof(buf), "%X", &tstruct);

    return buf;
}


vector<string> split(string str, string sep){
    char* cstr=const_cast<char*>(str.c_str());
    char* current;
    vector<string> arr;
    current=strtok(cstr,sep.c_str());
    while(current!=NULL){
        arr.push_back(current);
        current=strtok(NULL,sep.c_str());
    }
    cout << "__________________________SPLITTING________________________\n\n";
    for(int i=0; i<arr.size(); i++){
        cout<< arr[i] + "\n";
    }
    cout << "__________________________ ENDSPLIT________________________\n\n";
    return arr;
}


bool contains_Station(string routeLine, string destination){
    vector<string> ls = split(routeLine, ",");
    int indexOfLast = ls.size() - 1;
    if(ls[indexOfLast].compare(destination) == 0){
        return true;
    }
    else{
        return false;
    }
}


int main(int argc, char const *argv[]) 
{   
    // ARGUMENTS____________________________________________________________
    
    string stationName = argv[1];
    int PORT = stoi(argv[2]);
    int UDP_port = stoi(argv[3]);
    string neighbours[argc-4];
    
    for(int i=4; i<argc; i++){
        neighbours[i-4] = stoi(argv[i]);
    }
    
    // READING STATION INFO_________________________________________________
    string text;
    int numLines = 0;
    
    string flname = "tt-" + stationName + ".txt";
    cout << "____________________________txt file name \n";
    cout << flname + "\n\n";
    
    
    ifstream MyReadFile(flname);
    while(getline (MyReadFile, text)){
        routes[numLines] = text;
        routeList.push_back(text);
        numLines++;
    }
    MyReadFile.close();
    

    
    
    // NETWORKING____________________________________________________________
    char msg[] = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=ISO-8859-4 \r\n\r\n<html><body><h2>Welcome to Transperth</h2><img src='https://cdn.businessnews.com.au/styles/wabn_kb_company_logo/public/transperth.jpg?itok=8dMAeY3K' alt='transperth' width='384' height='80'><h4> Your route is as follows: <h4><hr>";

    int listenfd, connfd, udpfd, nready, maxfdp1; 
    char buffer[MAXLINE]; 
    pid_t childpid; 
    fd_set rset; 
    ssize_t n; 
    socklen_t len; 
    const int on = 1; 
    struct sockaddr_in cliaddr, servaddr; 
    void sig_chld(int); 
    char *message = "Hello, you connected to me!";
  
    /* create listening TCP socket */
    listenfd = socket(AF_INET, SOCK_STREAM, 0); 
    bzero(&servaddr, sizeof(servaddr)); 
    servaddr.sin_family = AF_INET; 
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY); 
    servaddr.sin_port = htons(PORT); 
  
    // binding server addr structure to listenfd 
    bind(listenfd, (struct sockaddr*)&servaddr, sizeof(servaddr)); 
    listen(listenfd, 10); 
  
    /* create UDP socket */
    udpfd = socket(AF_INET, SOCK_DGRAM, 0); 
    // binding server addr structure to udp sockfd 
    bind(udpfd, (struct sockaddr*)&servaddr, sizeof(servaddr)); 
  
    // clear the descriptor set 
    FD_ZERO(&rset); 
  
    // get maxfd 
    maxfdp1 = max(listenfd, udpfd) + 1; 
    for (;;) { 
  
        // set listenfd and udpfd in readset 
        FD_SET(listenfd, &rset); 
        FD_SET(udpfd, &rset); 
  
        // select the ready descriptor 
        nready = select(maxfdp1, &rset, NULL, NULL, NULL); 
  
        // if tcp socket is readable then handle 
        // it by accepting the connection 
        if (FD_ISSET(listenfd, &rset)) { 
            len = sizeof(cliaddr); 
            connfd = accept(listenfd, (struct sockaddr*)&cliaddr, &len); 
            if ((childpid = fork()) == 0) { 
                close(listenfd); 
                bzero(buffer, sizeof(buffer)); 
                printf("Message From TCP client: \n");
                read(connfd, buffer, sizeof(buffer));
                puts(buffer);
                
                // parse the get request
                const char *s = "\n";
                char *header;
                char *uri; 
                header = strtok(buffer, s);
                uri = getURI(header);
                
                string url = uri;
                string destinationStation = url.replace(0, 5, "");
                
                cout << "DestinationStation: \n";
                cout << destinationStation;
                cout << "\n\n";
                
                // CHECK FOR A DIRECT ROUTE FROM CURRENT STATION
                bool direct = isDirect(destinationStation);
                if(direct == true){
                    string now = currentDateTime();
                    cout << now + "\n\n";
                    
                    // scan all the routes
                    string lastRT;
                    string lastTime;
                    for(int i=1; i<routeList.size(); i++){
                        cout << routeList[i] + '\n';
                        char *rt = (char*) routeList[i].c_str();
                        char *time_c;
                        
                        time_c = strtok(rt, ",");
                        lastTime = time_c;
                        if(time_c < now){
                            bool check = contains_Station(routeList[i], destinationStation);
                            if(check){
                                cout << "IS CORRECT !\n";
                                lastRT = routeList[i];
                            }
                        }
                        else if(time_c >= now){
                            bool check = contains_Station(routeList[i], destinationStation);
                            if(check){
                                cout << "IS CORRECT !\n";
                                lastRT = routeList[i];
                                break;
                            }
                        }
                        else{
                            cout << "ERROR \n";
                        }
                    }
                    cout << "\n\n\n" + lastRT;
                    
                }
                send(connfd, msg, strlen(msg), 0);
                close(connfd); 
                exit(0);
            } 
        } 
        // if udp socket is readable receive the message. 
        if (FD_ISSET(udpfd, &rset)) { 
            len = sizeof(cliaddr); 
            bzero(buffer, sizeof(buffer)); 
            printf("\nMessage from UDP client: "); 
            n = recvfrom(udpfd, buffer, sizeof(buffer), 0, 
                         (struct sockaddr*)&cliaddr, &len); 
            puts(buffer); 
            sendto(udpfd, (const char*)message, sizeof(buffer), 0, 
                   (struct sockaddr*)&cliaddr, sizeof(cliaddr)); 
        } 
        close(connfd);
        break;
    } 
} 