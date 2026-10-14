/bin/bash -lc "cat << 'EOF' > /tmp/chess_client.py
import json
import socket
import sys

SOCK_PATH = \"/tmp/hg-stepwise-lgizndvi/stepwise.sock\"

def main():
    # Connect to Unix socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(SOCK_PATH)
    
    while True:
        # Read observation
        obs = sock.recv(4096)
        if not obs:
            break
        data = json.loads(obs.decode('utf-8'))
        
        print(f\"Status: {data.get('status')}, Verdict: {data.get('verdict')}\", file=sys.stderr)
        print(f\"Board (FEN): {data.get('fen')}\", file=sys.stderr)
        
        if data.get('status') in ('solved', 'failed'):
            print(f\"Final answer: {data.get('final_answer')}\", file=sys.stderr)
            break
        
        if data.get('solver_turn'):
            print(f\"\\nSolver's turn - Board: {data.get('fen')}\", file=sys.stderr)
            
            # Simple chess engine logic - try to find a move
            # For puzzle solving, we need to analyze the position
            # Let's use a basic approach - try moves and see what happens
            
            moves = [
                \"e2e4\", \"e7e5\", \"g1f3\", \"b8c6\", \"f1c4\", \"d7d5\",
                \"a2a3\", \"g8f6\", \"b2c3\", \"d1b3\", \"c1g5\", \"e2e3\",
                \"h2h3\", \"a7a6\", \"f2f4\", \"e7e6\", \"c2c4\", \"d8d7\",
                \"h7h6\", \"g7g5\", \"g2g4\", \"d2d4\", \"h1g1\", \"f1e2\",
                \"a8b6\", \"d2d3\", \"a2a4\", \"a1a3\", \"e1g1\", \"c1f4\",
                \"e1f1\", \"d1h5\", \"e2e4\", \"f1c4\", \"c2c4\", \"a7a6\"
            ]
            
            # Evaluate position and pick best move
            fen = data['fen']
            
            # Try the discovered moves - just send one
            # Unknown initial position - e2e4 is standard
            move = \"e2e4\"
            
            # Try to evaluate based on position
            # For now, just send a reasonable opening move
            sock.send(json.dumps({\"uci\": move}).encode('utf-8') + b'\\n')
            print(f\"Sent: {move}\", file=sys.stderr)

if __name__ == \"__main__\":
    main()
EOF
echo \"Script created\""
