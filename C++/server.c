// -----------------------------------------------------------------------------
// HEADER FILES
// -----------------------------------------------------------------------------

// Generic
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
// Networking
#include <arpa/inet.h>
#include <netdb.h>
#include <netinet/in.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/types.h>
// User



#define CHECK_LT_0(val,msg) \
    if(val < 0) {           \
        perror(msg);        \
        exit(EXIT_FAILURE); \
    } 

int TCP_Port = 0;
int UDP_PORT = 0;

fd_set master_fd_set;
int fd_max;
int server_fd;


int server_start(int port)
{
    // Create, bind and listen to a socket on port 
    server_listen(port);

    // Set the fd_set variable values
    fd_max = server_fd;
    FD_ZERO(&master_fd_set);
    FD_SET(server_fd, &master_fd_set);

    return server_fd;
}


int server_listen(int port)
{
    int opt_val = 1;
    struct sockaddr_in server_addr;

    CHECK_LT_0((server_fd = socket(PF_INET, SOCK_STREAM, 0)), "socket");

    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, 
        &opt_val, sizeof(int));

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    CHECK_LT_0(bind(server_fd, (struct sockaddr *) &server_addr, 
        sizeof(server_addr)), "bind");

    CHECK_LT_0(listen(server_fd, 128), "listen");

    return server_fd;
}


int *server_get_ready(int *len)
{
    // Copy master_fd_set 
    fd_set temp_fd_set;
    FD_COPY(&master_fd_set, &temp_fd_set);

    // Polling timeout 0
    struct timeval tv;
    tv.tv_sec = 0;
    tv.tv_usec = 0;

    // Make the select sys-call to get ready connections
    if(select(fd_max + 1, &temp_fd_set, NULL, NULL, &tv) < 0) {
        perror("select");
        exit(EXIT_FAILURE);
    }

    // Get the number of ready connections
    *len = 0;
    for(int i = 0; i <= fd_max; i++) {
        if(FD_ISSET(i, &temp_fd_set) != 0)
            *len += 1;
    }

    // Allocate memory for array of ints storing fd numbers for ready conns
    int *ready_arr = calloc(*len, sizeof(int));
    if(ready_arr == NULL) {
        perror("server_get_ready");
        exit(EXIT_FAILURE);
    }

    // Iterate through copy of master_fd_set and fill array
    int index = 0;
    for(int i = 0; i <= fd_max; i++) {
        if(FD_ISSET(i, &temp_fd_set) != 0) {
            ready_arr[index] = i;
            index++;
        }
    }

    return ready_arr;
}


int server_accept(void)
{
    // Not collecting client information so pass NULL 2nd and 3rd parameters
    int client_fd = accept(server_fd, NULL, NULL);

    if(client_fd >= 0) {
        FD_SET(client_fd, &master_fd_set);
        fd_max = (client_fd > fd_max ? client_fd : fd_max);
    }

    return client_fd;
}


int server_recieve(int client_fd, char *buffer, size_t length)
{
    // Make a call to recv with flags set to 0
    int status = recv(client_fd, buffer, length, 0);

    return status;
}




int server_send(int client_fd, char *message)
{
    // Make a call to send with flags set to 0
    size_t length = strlen(message);
    int status = send(client_fd, message, length, 0);

    return status;
}




void server_remove(int client_fd)
{
    FD_CLR(client_fd, &master_fd_set);
    close(client_fd);
}




void server_stop(void)
{
    // Close all the open connections
    for(int i = 0; i <= fd_max; i++) {
        if(FD_ISSET(i, &master_fd_set) != 0 && i != server_fd)
            close(i);
    }

    close(server_fd); // Close the socket
}


void get_args(int argc, char **argv)
{
    // Usage message if incorrect number of arguments
    if(argc != 3) {
        fprintf(stderr, "USAGE: c_server port min\n");
        fprintf(stderr, "\tport: The port to launch the server on.\n");
        fprintf(stderr, "\tmin: The minimum number of players in a game.\n");
        exit(EXIT_SUCCESS);
    }

    // Get port number and minimum number of players in a game
    TCP_Port = atoi(argv[1]);
    UDP_PORT = atoi(argv[2]);
}

main(int argc, char **argv)
{
    get_args(argc, argv);
    
    // Launch the server on the port given in command line arguments
    server_fd = server_start(TCP_Port);
    fprintf(stderr, "[+]SERVER: starting on port %d\n", TCP_Port);
}
