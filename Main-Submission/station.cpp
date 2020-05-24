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
#include <sstream>
#include <locale>

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



vector<string> split(string str, char sep){
    stringstream ss(str);
    vector<string> result;

    while( ss.good() )
    {
        string substr;
        getline(ss, substr, sep);
        result.push_back( substr );
    }
    for(int i=0; i<result.size(); i++){
        cout << result[i] + "\n";
    }
    return result;
}

string splitTime(string str, string sep, int index){
    stringstream ss(str);
    vector<string> result;

    while( ss.good() )
    {
        string substr;
        getline(ss, substr, ',');
        result.push_back( substr );
    }
    return result[index];
}


bool contains_Station(string routeLine, string destination){
    vector<string> ls = split(routeLine, ',');
    int indexOfLast = ls.size() - 1;
    if(ls[indexOfLast].compare(destination) == 0){
        return true;
    }
    else{
        return false;
    }
}

vector<string> neighNames(vector<string> rtList){
    vector<string> names;

    for(int i=0; i<rtList.size(); i++){
        vector<string> rt = split(rtList[0], ',');
        string neighName = rt[4];

        bool visited = false;
        for(int y=0; y<names.size(); y++){
            if(names[y].compare(neighName) == 0){
                visited = true;
                break;
            }
        }
        if(visited == false){
            names.push_back(neighName);
        }
    }
    return names;
}


vector<string> splitWhitespace(string str){

    std::vector<std::string> result;
    std::istringstream iss(str);
    for(std::string s; iss >> s; ){
        result.push_back(s);
    }
    return result;
}


int originalUDP(string uri){
    int start = uri.find("+");
    int end = uri.find("|");
    return stoi(uri.substr(start+1, end));
}


int main(int argc, char const *argv[]) 
{   
    // ARGUMENTS____________________________________________________________
    
    string stationName = argv[1];
    int PORT = stoi(argv[2]);
    int UDP_port = stoi(argv[3]);
    int neighbours[argc-4];
    
    for(int i=4; i<argc; i++){
        neighbours[i-4] = stoi(argv[i]);
        cout << "NEIGH: \n";
        cout << neighbours[i-4];
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
    routeList.erase(routeList.begin());
    MyReadFile.close();
    

    
    
    // NETWORKING____________________________________________________________
    char msg[] = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=ISO-8859-4 \r\n\r\n<html><body><h2>Welcome to Transperth</h2><img src='https://cdn.businessnews.com.au/styles/wabn_kb_company_logo/public/transperth.jpg?itok=8dMAeY3K' alt='transperth' width='384' height='80'><h4> Your route is as follows: <h4><hr>";
    string msgString = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=ISO-8859-4 \r\n\r\n<html><body><h2>Welcome to Transperth</h2><img src='https://cdn.businessnews.com.au/styles/wabn_kb_company_logo/public/transperth.jpg?itok=8dMAeY3K' alt='transperth' width='384' height='80'><h4> Your route is as follows: <h4><hr>";

    int listenfd, connfd, udpfd, nready, maxfdp1; 
    char buffer[MAXLINE]; 
    pid_t childpid; 
    fd_set rset; 
    ssize_t n; 
    socklen_t len; 
    const int on = 1; 
    struct sockaddr_in cliaddr, servaddr; 
    void sig_chld(int);
  
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
    
     struct sockaddr_in serverAddr;
        /* Construct local udp address structure */
        memset(&serverAddr, 0, sizeof(serverAddr));   /* Zero out structure */
        serverAddr.sin_family = AF_INET;                /* Internet address family */
        serverAddr.sin_addr.s_addr = htonl(INADDR_ANY); /* Any incoming interface */
        serverAddr.sin_port = htons(UDP_port);      /* Local port */
        
        
    // binding server addr structure to udp sockfd 
    bind(udpfd, (struct sockaddr*)&serverAddr, sizeof(serverAddr)); 
    
    
    
    
  
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
                string head = header;
                vector<string> headerInfo = splitWhitespace(head);
                
                string url = headerInfo[1];
                string destinationStation = url.replace(0, 5, "");
                
                cout << "DestinationStation: \n";
                cout << destinationStation;
                cout << "\n\n";
                
                // CHECK FOR A DIRECT ROUTE FROM CURRENT STATION
                bool direct = isDirect(destinationStation);
                if(direct == true){
                    printf("IS DIRECT __________:");
                    string now = currentDateTime();
                    cout << now + "\n\n";
                    
                    // scan all the routes
                    string lastRT;
                    string lastTime;
                    for(int i=1; i<routeList.size(); i++){
                        string time_c = splitTime(routeList[i], ",", 0);
                        cout << "\n\n\ntime_c: " + time_c + "\n\n\n";
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

                    vector<string> rt = split(lastRT, ',');
                    string departureTime = rt[0];
                    string busNum = rt[1];
                    string stop = rt[2];
                    string arrivalTime = rt[3];
                    string startStation = rt[4];

                    string appendString = "<p>From: " + stationName + "</p>" + "<p>To: " + destinationStation + "</p>" + "<p> Boarding Time: " + departureTime + "</p>" + "<p> Number: " + busNum + "</p>" + "<p> Stop: " + stop + "</p>" + "<p> Arrival Time: " + arrivalTime + "</p>";
                    msgString.append(appendString);
                    char *toSend = (char *) msgString.c_str();
                    send(connfd, toSend, strlen(toSend), 0);
                    close(connfd); 
                    exit(0);
                }
                else{
                    // not a direct route, so send UDP message with new appended protocol uri 
                    string now = currentDateTime();
                    string nextRouteToEachNeighbour[argc-4];
                    vector<string> neiNames = neighNames(routeList);

                    
                    for(int i=0; i<argc-4; i++){
                        // scan all the routes
                        string lastRT;
                        string lastTime;
                        for(int y=0; y<routeList.size(); y++){
                            string time_c = splitTime(routeList[i], ",", 0);
                            cout << "\n\n\ntime_c: " + time_c + "\n\n\n";
                            if(time_c < now){
                            bool check = contains_Station(routeList[y], neiNames[i]);
                                if(check){
                                cout << "IS CORRECT !\n";
                                lastRT = routeList[i];
                                }
                            }
                            else if(time_c >= now){
                                bool check = contains_Station(routeList[y], neiNames[i]);
                                if(check){
                                    cout << "You are able to use this time/route !\n";
                                    lastRT = routeList[i];
                                    break;
                                }
                            }
                            else{
                                cout << "ERROR \n";
                            }
                        }
                        nextRouteToEachNeighbour[i] = lastRT;
                    }

                    for(int r=0; r<argc-4; r++){
                        cout << "this loop\n\n";
                        if(nextRouteToEachNeighbour[r].length() == 0){
                            cout << "\n" + to_string(neighbours[r]) + "\n";
                            cout << "\n\n---YOU MISSED THE LAST BUS, THERE ARE NO BUSSES TODAY (NO DIRECT ROUTE NOW)----\n\n";
                        }
                        else{
                            cout << "This statement\n\n";

                            struct sockaddr_in addr;
                            memset(&addr, 0, sizeof(addr));
                            addr.sin_family = AF_INET;
                            addr.sin_addr.s_addr = htonl(INADDR_ANY);
                            addr.sin_port = htons(neighbours[r]);

                            vector<string> rt = split(nextRouteToEachNeighbour[r], ',');
                            string arvlTime = rt[3];
                            string depTime = rt[0];

                            string protocolMessage = "/?to=" + url + "&through=" + stationName + "%" + depTime + ">" + arvlTime + "+" + to_string(UDP_port) + "|";
                            cout << protocolMessage;
                            char *sendMsg = (char *) protocolMessage.c_str();

                            cout<< "\n\n  NEIGHBOURS LENGTH: \n\n";

                            sendto(udpfd, sendMsg, 1024, 0, (struct sockaddr*)&addr, sizeof(serverAddr)); 
                        }
                    }
                } 
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
            // sendto(udpfd, (const char*)message, sizeof(buffer), 0, (struct sockaddr*)&cliaddr, sizeof(cliaddr)); 

            string rqst = buffer;
            if(rqst.find("<p>") != -1){
                cout << "SEND TO CLIENT";
                send(connfd, buffer, strlen(buffer), 0);
            }

            vector<string> ls = split(buffer, '=');
            vector<string> stations;
            ls.erase(ls.begin());

            for(int i=0; i<ls.size(); i++){
                if(ls[i].find("&") != -1){
                    int index = ls[i].find("&");
                    string finalNeigh = ls[i].substr(0, index);
                    stations.push_back(finalNeigh);
                }
                else if(ls[i].find("%") != -1){
                    int pos = ls[i].find("%");
                    string t_neigh = ls[i].substr(0, pos);
                    stations.push_back(t_neigh);
                }
            }
            bool directRt = isDirect(stations[0]);
            if(directRt == true){
                    printf("IS DIRECT __________:");
                    string now = currentDateTime();
                    cout << now + "\n\n";
                    
                    // scan all the routes
                    string lastRT;
                    string lastTime;
                    for(int i=1; i<routeList.size(); i++){
                        string time_c = splitTime(routeList[i], ",", 0);
                        cout << "\n\n\ntime_c: " + time_c + "\n\n\n";
                        if(time_c < now){
                            bool check = contains_Station(routeList[i], stations[0]);
                            if(check){
                                cout << "IS CORRECT !\n";
                                lastRT = routeList[i];
                            }
                        }
                        else if(time_c >= now){
                            bool check = contains_Station(routeList[i], stations[0]);
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

                    vector<string> rt = split(lastRT, ',');
                    string departureTime = rt[0];
                    string busNum = rt[1];
                    string stop = rt[2];
                    string arrivalTime = rt[3];
                    string startStation = rt[4];

                    string appendString = "<p>From: " + stationName + "</p>" + "<p>To: " + stations[0] + "</p>" + "<p> Boarding Time: " + departureTime + "</p>" + "<p> Number: " + busNum + "</p>" + "<p> Stop: " + stop + "</p>" + "<p> Arrival Time: " + arrivalTime + "</p>";
                    char *toSend = (char *) appendString.c_str();

                    int orig = originalUDP(buffer);
                    struct sockaddr_in oaddr;
                    memset(&oaddr, 0, sizeof(oaddr));
                    oaddr.sin_family = AF_INET;
                    oaddr.sin_addr.s_addr = htonl(INADDR_ANY);
                    oaddr.sin_port = htons(orig);

                    cout << "OriginalPort";
                    cout << "\n"+ to_string(orig) + "\n\n";
                    cout << toSend;
                    cout << "\n\n\n";

                    sendto(udpfd, toSend, 1024, 0, (struct sockaddr*)&oaddr, sizeof(serverAddr)); 
                }
        } 
    } 
} 