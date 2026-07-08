import sqlite3

def main():
    try:
        conn = sqlite3.connect("aimf.db")
        c = conn.cursor()
        c.execute("SELECT count(*) FROM channels;")
        channels = c.fetchone()[0]
        c.execute("SELECT count(*) FROM videos;")
        videos = c.fetchone()[0]
        c.execute("SELECT count(*) FROM jobs;")
        jobs = c.fetchone()[0]
        
        # also check audio_path exists
        c.execute("PRAGMA table_info(videos);")
        columns = [col[1] for col in c.fetchall()]
        audio_path_exists = "audio_path" in columns
        
        print(f"Channels: {channels}")
        print(f"Videos: {videos}")
        print(f"Jobs: {jobs}")
        print(f"Videos.audio_path exists: {audio_path_exists}")
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    main()
