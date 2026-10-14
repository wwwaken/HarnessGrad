exec((__import__('pathlib').Path(__file__).resolve().parent/'acquire-recorded.py').read_text().split("body,status=fetch")[0])
j=json.loads((root/'github-tag.body').read_bytes());sha=j['object']['sha']
b,s=fetch('github-commit',f'https://api.github.com/repos/open-thought/reasoning-gym/git/commits/{sha}')
assert s==200
commit=json.loads(b);tree=commit['tree']['sha']
b,s=fetch('github-tree',f'https://api.github.com/repos/open-thought/reasoning-gym/git/trees/{tree}?recursive=1')
assert s==200
