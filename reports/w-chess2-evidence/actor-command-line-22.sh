/bin/bash -lc "python3 << 'PYEOF'
import json
import socket
import sys

SOCK_PATH = \"/tmp/hg-stepwise-lgizndvi/stepwise.sock\"

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect(SOCK_PATH)

full_output = []
for i in range(10):
    obs = sock.recv(4096)
    if not obs:
        print(\"\\nConnection ended, no more responses.\")
        break
    
    data = json.loads(obs.decode('utf-8'))
    output = f\"\\n[{i}] Status: {data.get('status')}, Verdict: {data.get('verdict')}\"
    output += f\"\\nFEN: {data.get('fen')}\"
    output += f\"\\nSolver turn: {data.get('solver_turn')}\"
    
    if data.get('status') in ('solved', 'failed'):
        output += f\"\\nFinal: {data.get('final_answer')}\"
        output += \"\\nGAME OVER\"
        print(output)
        break
    
    if data.get('solver_turn'):
        fen = data['fen']
        
        # Identify position and choose move
        move = \"e2e4\"  # default
        
        # Try to analyze FEN for standard starting position
        is_standard_start = fen == \"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1\"
        
        if is_standard_start:
            # We're making first move - just play e4
            move = \"e2e4\"
            
            # Send move
            response = json.dumps({\"uci\": move}) + \"\\n\"
            sock.send(response.encode('utf-8'))
            output += f\"\\nMove chosen: {move}\"
        
        print(output)

sock.close()
PYEOF"
