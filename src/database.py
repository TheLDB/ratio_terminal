import os.path
import sqlite3
from contextlib import suppress

from enums.leaderboard_order import LeaderboardOrder
from models.leaderboard_entry import LeaderboardEntry
from models.score import Score
from models.server_info import ServerInfo


class Database:
    def __init__(self):
        self.con = sqlite3.connect(os.path.join('data', 'leaderboard.db'))
        self.cur = self.con.cursor()

        self.cur.execute("CREATE TABLE IF NOT EXISTS leaderboard ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "user_id TEXT, "
                    "server_id TEXT, "
                    "score INTEGER DEFAULT 0, "
                    "accepted_score INTEGER DEFAULT 0, "
                    "declined_score INTEGER DEFAULT 0)")

        self.cur.execute("CREATE TABLE IF NOT EXISTS data ("
                    "key TEXT PRIMARY KEY, "
                    "value TEXT)")

        self.cur.execute("CREATE TABLE IF NOT EXISTS server_settings ("
                    "id INTEGER PRIMARY KEY, "
                    "key TEXT, "
                    "value TEXT)")

        # Perform database upgrades
        with suppress(Exception):
            ## leaderboard: ADD accepted_score, declined_score
            self.cur.execute("ALTER TABLE leaderboard ADD COLUMN accepted_score INT default 0")
            self.cur.execute("UPDATE leaderboard SET accepted_score = score")
            self.cur.execute("ALTER TABLE leaderboard ADD COLUMN declined_score INT default 0")
        
        self.con.commit()

    def __parse_lb_entry__(self, data: dict[any]) -> LeaderboardEntry:
        return LeaderboardEntry(data[0], data[1], data[2], data[3], data[4], data[5])

    def get_user_server_data(self, user_id: str, server_id: str) -> LeaderboardEntry:
        data = self.cur.execute("SELECT * FROM leaderboard WHERE user_id = ? AND server_id = ?", [user_id, server_id]).fetchone()
        
        # Create a record if it doesn't exist
        if data is None:
            self.cur.execute("INSERT INTO leaderboard VALUES(NULL, ?, ?, 0, 0, 0)", [user_id, server_id])
            return LeaderboardEntry(self.cur.lastrowid, user_id) # uhhhhh 
        
        return self.__parse_lb_entry__(data)

    def get_user_global(self, user_id: str) -> Score:
        scores = self.cur.execute("SELECT accepted_score, declined_score FROM leaderboard WHERE user_id = ?", [user_id]).fetchall()
        accepted_ratios = 0
        declined_ratios = 0
        for r in scores:
            accepted_ratios += r[0]
            declined_ratios += r[1]
        return Score(accepted_ratios, declined_ratios)
    
    def get_server(self, server_id: int, order: LeaderboardOrder, limit: int) -> ServerInfo:
        # So... can't use ? to pass order.value because it fucking dies
        query = self.cur.execute(f"SELECT * FROM leaderboard WHERE server_id = ? ORDER BY score {order.value}",
                            [server_id]).fetchmany(limit)

        total_accepted = 0
        total_declined = 0
        leaderboard = list[LeaderboardEntry]()
        
        for entry in query:
            data: LeaderboardEntry = self.__parse_lb_entry__(entry)
            leaderboard.append(data)
            total_accepted += data.accepted_score
            total_declined += data.declined_score

        total = total_accepted - total_declined
        ratio_accepted = round((total_accepted / (total)) * 100, 1)
        ratio_declined = 100 - ratio_accepted

        return ServerInfo(leaderboard, ratio_accepted, ratio_declined, total_accepted, total_declined, total)
    
    def change_score(self, user_id: str, server_id: str, is_accepted: bool):
        user_data: LeaderboardEntry = self.get_user_server_data(user_id, server_id)

        accepted_score = user_data.accepted_score + 1 if is_accepted else user_data.accepted_score
        declined_score = user_data.declined_score + 1 if not is_accepted else user_data.declined_score
        score = accepted_score - declined_score

        self.cur.execute('UPDATE leaderboard SET score = ?, accepted_score = ?, declined_score = ? WHERE id = ?', 
                    [score, accepted_score, declined_score, user_data.id])
        self.con.commit()

    def __set_value(self, key: str, value: str):
        self.cur.execute(f'INSERT OR REPLACE INTO data VALUES({key}, {value})')

    def __get_value(self, key: str) -> str:
        return self.cur.execute(f'SELECT value FROM data WHERE key = {key}').fetchone()
