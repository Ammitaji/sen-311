import sqlite3

def backup_database():
    # Connect to current database
    source = sqlite3.connect('database.db')
    
    # Create backup file
    with open('database_backup.sql', 'w') as f:
        for line in source.iterdump():
            f.write(f'{line}\n')
    
    source.close()
    print("Backup created: database_backup.sql")

if __name__ == '__main__':
    backup_database()