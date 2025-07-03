#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>
#include <sys/stat.h>  // For mkdir

#define CUSTOM_FOLDER "C:\\Users\\DELL\\Desktop\\secure folder"

void create_user_file(const char *username) {
    char filename[256];
    char user_filename[400];

    printf("Enter the name of the file to create (without extension): ");
    scanf("%255s", filename);

    snprintf(user_filename, sizeof(user_filename), "%s\\%s_%s.txt", CUSTOM_FOLDER, username, filename);

    FILE *fp = fopen(user_filename, "w");
    if (fp == NULL) {
        printf("Error creating file.\n");
        return;
    }
    fprintf(fp, "Welcome %s! This is your file: %s\n", username, user_filename);
    fclose(fp);

    printf("File %s created successfully in folder.\n", user_filename);
}

void read_user_file(const char *username) {
    char filename[256];
    char user_filename[400];

    printf("Enter the name of the file to read (without extension): ");
    scanf("%255s", filename);
    snprintf(user_filename, sizeof(user_filename), "%s\\%s_%s.txt", CUSTOM_FOLDER, username, filename);

    FILE *fp = fopen(user_filename, "r");
    if (fp == NULL) {
        printf("No file found in folder. Access denied.\n");
        return;
    }

    char ch;
    printf("Reading file contents from %s:\n", user_filename);
    while ((ch = fgetc(fp)) != EOF)
        putchar(ch);
    fclose(fp);
}

void write_user_file(const char *username) {
    char filename[256];
    char user_filename[400];

    printf("Enter the name of the file to write (without extension): ");
    scanf("%255s", filename);
    snprintf(user_filename, sizeof(user_filename), "%s\\%s_%s.txt", CUSTOM_FOLDER, username, filename);

    FILE *fp = fopen(user_filename, "a");
    if (fp == NULL) {
        printf("No file found in folder. Access denied.\n");
        return;
    }

    char buffer[256];
    printf("Enter text to append (end with a single line containing only 'END'):\n");
    getchar(); // consume leftover newline
    while (1) {
        fgets(buffer, sizeof(buffer), stdin);
        buffer[strcspn(buffer, "\n")] = 0;
        if (strcmp(buffer, "END") == 0)
            break;
        fprintf(fp, "%s\n", buffer);
    }
    fclose(fp);
    printf("Text written to %s\n", user_filename);
}

void access_all_files() {
    int mode;
    printf("1. List and select file from %s folder\n2. Enter filename manually\nChoose option: ", CUSTOM_FOLDER);
    scanf("%d", &mode);
    getchar(); // consume newline

    if (mode == 1) {
        WIN32_FIND_DATAA findFileData;
        HANDLE hFind;
        char search_path[500];
        int count = 0;
        char files[100][256];

        snprintf(search_path, sizeof(search_path), "%s\\*.txt", CUSTOM_FOLDER);
        hFind = FindFirstFileA(search_path, &findFileData);
        if (hFind == INVALID_HANDLE_VALUE) {
            printf("No .txt files found in %s folder.\n", CUSTOM_FOLDER);
            return;
        }
        do {
            printf("%d. %s\n", count + 1, findFileData.cFileName);
            strcpy(files[count], findFileData.cFileName);
            count++;
            if (count >= 100) break;
        } while (FindNextFileA(hFind, &findFileData));
        FindClose(hFind);

        if (count == 0) {
            printf("No .txt files found in %s folder.\n", CUSTOM_FOLDER);
            return;
        }

        int choice;
        printf("Enter file number to read (0 to cancel): ");
        scanf("%d", &choice);
        getchar(); // consume newline
        if (choice < 1 || choice > count) {
            printf("Cancelled or invalid choice.\n");
            return;
        }

        char full_path[500];
        snprintf(full_path, sizeof(full_path), "%s\\%s", CUSTOM_FOLDER, files[choice - 1]);
        FILE *fp = fopen(full_path, "r");
        if (!fp) {
            printf("Error opening file.\n");
            return;
        }
        printf("Contents of %s:\n", full_path);
        char ch;
        while ((ch = fgetc(fp)) != EOF)
            putchar(ch);
        fclose(fp);
    } else if (mode == 2) {
        char filename[300];
        char full_path[500];
        printf("Enter the exact name of the file to read (including .txt): ");
        scanf("%299s", filename);
        snprintf(full_path, sizeof(full_path), "%s\\%s", CUSTOM_FOLDER, filename);

        FILE *fp = fopen(full_path, "r");
        if (!fp) {
            printf("Error opening file '%s' in %s folder.\n", filename, CUSTOM_FOLDER);
            return;
        }
        printf("Contents of %s:\n", full_path);
        char ch;
        while ((ch = fgetc(fp)) != EOF)
            putchar(ch);
        fclose(fp);
    } else {
        printf("Invalid option.\n");
    }
}

int main(int argc, char *argv[]) {
    char role[20];
    char username[100];

    if (argc >= 3) {
        strncpy(role, argv[1], sizeof(role) - 1);
        role[sizeof(role) - 1] = '\0';
        strncpy(username, argv[2], sizeof(username) - 1);
        username[sizeof(username) - 1] = '\0';
        printf("Welcome %s! Role: %s\n", username, role);
    } else {
        printf("Usage: %s <role> <username>\n", argv[0]);
        return 1;
    }

    int choice;
    if (strcmp(role, "admin") == 0) {
        while (1) {
            printf("\n1. Create Secure File\n");
            printf("2. Read Secure File\n");
            printf("3. Write to Secure File\n");
            printf("4. Access all files (admin only)\n");
            printf("5. Exit\n");
            printf("Enter your choice: ");
            scanf("%d", &choice);
            getchar(); // consume newline

            if (choice == 1)
                create_user_file(username);
            else if (choice == 2)
                read_user_file(username);
            else if (choice == 3)
                write_user_file(username);
            else if (choice == 4)
                access_all_files();
            else if (choice == 5) {
                printf("Exiting...\n");
                break;
            }
            else
                printf("Invalid choice.\n");
        }
    } else if (strcmp(role, "user") == 0) {
        while (1) {
            printf("\n1. Create Secure File\n");
            printf("2. Read Secure File\n");
            printf("3. Write to Secure File\n");
            printf("4. Exit\n");
            printf("Enter your choice: ");
            scanf("%d", &choice);
            getchar(); // consume newline

            if (choice == 1)
                create_user_file(username);
            else if (choice == 2)
                read_user_file(username);
            else if (choice == 3)
                write_user_file(username);
            else if (choice == 4) {
                printf("Exiting...\n");
                break;
            }
            else
                printf("Invalid choice.\n");
        }
    } else {
        printf("Invalid role. Exiting...\n");
    }
    return 0;
}