import socket
import threading
import json
import sys

class TicTacToe3DServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(2)
        print(f"Server listening on {host}:{port}")
        
        # Game state
        self.jugadas = [[[0 for _ in range(4)] for _ in range(4)] for _ in range(4)]
        self.players = []
        self.current_player = 0  # 0 for player 1 (X), 1 for player 2 (O)
        self.game_over = False
        self.winner = None
        
        # Win conditions
        self.C = [[1, 1, 0], [1, 0, 1], [0, 1, 1], [1, 0, 0],
                 [1, -1, 0], [0, 0, 1], [-1, 0, 1], [0, 1, 0],
                 [0, 1, -1], [0, -1, -1], [0, -1, 0], [0, 0, -1],
                 [0, 0, 0]]
        
        self.lock = threading.Lock()
    
    def handle_client(self, client_socket, player_id):
        """Handle individual client connection"""
        try:
            # Send player ID to client
            init_data = {
                'type': 'init',
                'player_id': player_id,
                'player_name': f'Player {player_id + 1}',
                'symbol': 'X' if player_id == 0 else 'O'
            }
            client_socket.send(json.dumps(init_data).encode())
            
            # Send initial game state
            self.send_game_state(client_socket)
            
            while True:
                try:
                    # Receive move from client
                    data = client_socket.recv(1024).decode()
                    if not data:
                        break
                    
                    message = json.loads(data)
                    
                    if message['type'] == 'move':
                        with self.lock:
                            if not self.game_over and message['player'] == self.current_player:
                                z, y, x = message['z'], message['y'], message['x']
                                
                                # Validate move
                                if self.jugadas[z][y][x] == 0:
                                    # Make move (-1 for X, 1 for O)
                                    self.jugadas[z][y][x] = -1 if self.current_player == 0 else 1
                                    
                                    # Check for win
                                    win_result = self.check_win(z, y, x)
                                    if win_result:
                                        self.game_over = True
                                        self.winner = self.current_player
                                        self.send_game_state_to_all()
                                    else:
                                        # Check for draw
                                        if self.is_draw():
                                            self.game_over = True
                                            self.winner = -1  # Draw
                                            self.send_game_state_to_all()
                                        else:
                                            # Switch player
                                            self.current_player = 1 - self.current_player
                                            self.send_game_state_to_all()
                                else:
                                    # Invalid move
                                    error_msg = {
                                        'type': 'error',
                                        'message': 'Invalid move - cell already occupied'
                                    }
                                    client_socket.send(json.dumps(error_msg).encode())
                    
                    elif message['type'] == 'reset':
                        with self.lock:
                            self.reset_game()
                            self.send_game_state_to_all()
                    
                    elif message['type'] == 'disconnect':
                        break
                        
                except (json.JSONDecodeError, KeyError):
                    pass
                    
        except Exception as e:
            print(f"Error with player {player_id}: {e}")
        finally:
            with self.lock:
                if client_socket in self.players:
                    self.players.remove(client_socket)
            client_socket.close()
            print(f"Player {player_id} disconnected")
            
            # If one player disconnects, end the game
            self.game_over = True
            self.send_game_state_to_all()
    
    def check_win(self, z, y, x):
        """Check if the last move resulted in a win"""
        player_value = -1 if self.current_player == 0 else 1
        
        for c in self.C:
            tz, ty, tx = c
            z1 = z if tz > 0 else -1
            y1 = y if ty > 0 else -1
            x1 = x if tx > 0 else -1
            s = 0
            
            for i in range(4):
                z_pos = z if z1 >= 0 else (3 - i if tz else i)
                y_pos = y if y1 >= 0 else (3 - i if ty else i)
                x_pos = x if x1 >= 0 else (3 - i if tx else i)
                s += self.jugadas[z_pos][y_pos][x_pos]
            
            if abs(s) == 4:  # All 4 cells belong to same player
                return True
        return False
    
    def is_draw(self):
        """Check if the game is a draw"""
        for z in range(4):
            for y in range(4):
                for x in range(4):
                    if self.jugadas[z][y][x] == 0:
                        return False
        return True
    
    def reset_game(self):
        """Reset the game state"""
        self.jugadas = [[[0 for _ in range(4)] for _ in range(4)] for _ in range(4)]
        self.current_player = 0
        self.game_over = False
        self.winner = None
    
    def send_game_state(self, client_socket):
        """Send current game state to a specific client"""
        game_state = {
            'type': 'state',
            'jugadas': self.jugadas,
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner
        }
        client_socket.send(json.dumps(game_state).encode())
    
    def send_game_state_to_all(self):
        """Send current game state to all connected clients"""
        game_state = {
            'type': 'state',
            'jugadas': self.jugadas,
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner
        }
        
        for client in self.players:
            try:
                client.send(json.dumps(game_state).encode())
            except:
                pass
    
    def run(self):
        """Main server loop to accept connections"""
        player_id = 0
        while True:
            if len(self.players) < 2:
                client, addr = self.server.accept()
                print(f"New connection from {addr}, assigned Player {player_id + 1}")
                
                self.players.append(client)
                
                # Create thread for this client
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client, player_id)
                )
                thread.daemon = True
                thread.start()
                
                # If we have 2 players, start the game
                if len(self.players) == 2:
                    print("Two players connected! Starting game...")
                    self.send_game_state_to_all()
                
                player_id = 1 - player_id  # Toggle between 0 and 1 for next player

if __name__ == "__main__":
    # Get host and port from command line arguments or use defaults
    host = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5555
    
    server = TicTacToe3DServer(host, port)
    server.run()