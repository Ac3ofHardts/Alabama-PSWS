#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
	setuid(0);

	if(argc != 3) {
		printf("Incorrect usage");
		exit(1);
	}

	char command1[20];
	char command2[75];

	char useradd[10], echo[10], passwd[20];

	strcpy(useradd, "useradd ");
	strcpy(echo, "echo -n ");
	strcpy(passwd, " | passwd --stdin ");

	strcpy(command1, useradd);
	strncat(command1, argv[1], 8);

	strcpy(command2, echo);
	strncat(command2, argv[2], 32);
	strncat(command2, passwd, 19);
	strncat(command2, argv[1], 8);

	command1[15] = '\0';
	command2[65] = '\0';
	
	system(command1);
	system(command2);

	char command3[28];
	char usermod[21];
	strcpy(usermod, "usermod -g stations ");
	strcpy(command3, usermod);
	strncat(command3, argv[1], 8);
	system(command3);

	char command4[24];
	char chmod[17];
	strcpy(chmod, "chmod g+x /home/");
	strcpy(command4, chmod);
	strncat(command4, argv[1], 8);
	system(command4);

	exit(0);
}
