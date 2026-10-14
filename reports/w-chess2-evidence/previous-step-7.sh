python3 << 'EOF'
import socket
import json
import sys
import chess

sock_path = '/tmp/hg-stepwise-74i44xz0/stepwise.sock'

try:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(sock_path)
    
    # Read observation
    data = sock.recv(4096)
    obs = json.loads(data.decode('utf-8'))
    
    fen = obs['fen']
    solver_turn = obs['solver_turn']
    status = obs['status']
    
    print(f"FEN: {fen}")
    print(f"Status: {status}")
    print(f"Solver turn: {solver_turn}")
    
    # Parse FEN
    board = chess.Board(fen)
    print(f"Board:")
    print(board)
    print(f"Turn: {board.turn}")
    
    # Find best move
    # This is a chess puzzle, so we need to find the winning move
    # Let's use a simple approach: find all legal moves and evaluate them
    
    # For now, let's just print legal moves
    legal_moves = list(board.legal_moves)
    print(f"Number of legal moves: {len(legal_moves)}")
    
    # Let's analyze the position
    # FEN: 5rk1/1R3p1p/p5p1/5n2/PPQ1p3/4P3/3q1PPP/2R3K1 b - - 2 29
    # It's Black's turn
    
    # Let's try to find a good move
    # We'll use a simple evaluation function
    
    best_move = None
    best_score = float('-inf')
    
    for move in legal_moves:
        board.push(move)
        # Simple material evaluation
        score = board.evaluate()
        board.pop()
        
        if score > best_score:
            best_score = score
            best_move = move
    
    print(f"Best move: {best_move}")
    print(f"Best score: {best_score}")
    
    # Send the move
    move_str = chess.Move.to_san(best_move)
    print(f"Sending move: {move_str}")
    
    answer = {"uci": move_str}
    sock.sendall(json.dumps(answer).encode('utf-8') + b'\n')
    
    # Read response
    response = sock.recv(4096)
    if response:
        resp = json.loads(response.decode('utf-8'))
        print(f"Response: {json.dumps(resp, indent=2)}")
        
        # Check if solved
        if resp.get('status') == 'solved':
            print("Puzzle solved!")
            sys.exit(0)
        elif resp.get('status') == 'failed':
            print("Puzzle failed!")
            sys.exit(0)
    
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()
EOF
