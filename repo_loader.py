import sys
import os
import fnmatch
from pathlib import Path
import re
import nbformat
from collections import defaultdict
 
SEPARATOR = "=" * 48
 
try:
    PATH = Path(__file__).resolve()
except NameError:
    PATH = Path(sys.argv[0]).resolve()
 
IGNORE_PATTERNS = [
    # js, java, python, c, c++, c#, .net, go, rust, swift, ruby
    "*.pyc", "*.pyo", "*.pyd", "__pycache__", ".pytest_cache", ".ipynb_checkpoints", ".coverage", ".mypy_cache", ".ruff_cache", ".tox", ".nox", "poetry.lock", "Pipfile.lock","node_modules", "bower_components", "package-lock.json", "yarn.lock", ".npm", ".yarn", ".pnpm-store", "bun.lock", "bun.lockb","*.class", "*.jar", "*.war", "*.ear", "*.nar","*.o", "*.obj", "*.dll", "*.dylib", "*.exe", "*.lib", "*.out", "*.a", "*.pdb","obj", "*.suo", "*.user", "*.userosscache", "*.sln.docstates", "*.nupkg","pkg","Cargo.lock", "*.rs.bk","*.gem", ".bundle",".build", "*.xcodeproj", "*.xcworkspace", "*.pbxuser", "*.mode1v3", "*.mode2v3", "*.perspectivev3", "*.xcuserstate", "xcuserdata", ".swiftpm",
    # dependencies & builds
    "build", "dist", "out", "target", "vendor", "bin","venv", ".venv", "env", "virtualenv","*.egg-info", "*.egg", "*.whl", "*.so",
    # version
    ".git", ".svn", ".hg", ".gitignore", ".gitattributes", ".gitmodules", "digest.txt",
    # ide & editor
    ".idea", ".vscode", ".vs", ".project", "*.swo", "*.swn", "*.sublime-*",
    # vnvironment & credentials
    ".env", ".env.*", "credentials.json", "aws_credentials", "id_rsa", "*.pem", "*.key",
    # media & docs
    "*.svg", "*.png", "*.jpg", "*.jpeg", "*.gif", "*.ico","*.pdf", "*.mov", "*.mp4", "*.mp3", "*.wav","site-packages", ".docusaurus", ".next", ".nuxt",
    # temp & cache
    "*.log", "*.bak", "*.swp", "*.tmp", "*.temp", ".cache", ".sass-cache", ".eslintcache", ".DS_Store", "Thumbs.db", "desktop.ini",
    # database
    "*.db", "*.sqlite", "*.sqlite3", "*.tfstate*",
    # other
    "*.zip","*.min.js","*.min.css","*.map","context.txt","*.csv","*.xlsx","*.xlsm","*.xlsb","*.xltx","*.xltm","*.xlam",
 
    # --- add files or directories you want to ignore ---
    "specfic_folder/", "specfic_file.py",
]
 
SECRET_PATTERNS = [
    # aws, google, azure
    re.compile(r'AKIA[0-9A-Z]{16}'),re.compile(r'ASIA[0-9A-Z]{16}'),re.compile(r'AGPA[0-9A-Z]{16}'),re.compile(r'ACCA[0-9A-Z]{16}'),re.compile(r'AIza[0-9A-Za-z\-_]{35}'),re.compile(r'ya29\.[0-9A-Za-z\-_]+'),re.compile(r'^[A-Za-z0-9_-]{24}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27}$'),
    # paas, payment
    re.compile(r'heroku[a-f0-9]{32}'),re.compile(r'sk_live_[0-9a-zA-Z]{24}'),re.compile(r'sk_test_[0-9a-zA-Z]{24}'),
    # email, monitoring
    re.compile(r'SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}'),re.compile(r'https://[0-9a-f]+@[0-9]+\.ingest\.sentry\.io/[0-9]+'),re.compile(r'NRII\-[A-F0-9]{25}'),re.compile(r'dd_api_key\s*=\s*["\'][A-Za-z0-9]{32}["\']', re.IGNORECASE),re.compile(r'dd_application_key\s*=\s*["\'][A-Za-z0-9]{40}["\']', re.IGNORECASE),
    # version
    re.compile(r'gh[pousr]_[A-Za-z0-9]{36}'),re.compile(r'glpat-[A-Za-z0-9\-_]{20,}'),
    # communication
    re.compile(r'xoxo[apbrs]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}'),re.compile(r'https://hooks\.slack\.com/services/[A-Za-z0-9/_\-]+'),re.compile(r'xox[bp]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[A-Za-z0-9]{24}'),
    # telephony
    re.compile(r'AC[0-9a-f]{32}'),re.compile(r'[0-9a-f]{32}'),
    # auth (jwt, basic auth, generic)
    re.compile(r'eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+'),re.compile(r'Authorization\s*:\s*Basic\s+[A-Za-z0-9+/=]+', re.IGNORECASE),re.compile(r'(?:session|auth)[_-]?token\s*[:=]\s*["\'][A-Za-z0-9\-_\.]+["\']', re.IGNORECASE),
    # db conn
    re.compile(r'(?:mongodb\+srv|postgresql?|mysql)://[^ \n]+'),
    # ssh
    re.compile(r'ssh-(rsa|ed25519)\s+AAAA[0-9A-Za-z+/=]+'),
    # certs
    re.compile(r'\.pem$'),re.compile(r'\.key$'),re.compile(r'-----BEGIN (?:RSA )?PRIVATE KEY-----'),re.compile(r'-----BEGIN CERTIFICATE-----'),re.compile(r'-----BEGIN PKCS12-----'),
    # generic keys & pw
    re.compile(r'\bAPI_KEY\s*=\s*["\'][^"\']+["\']'),re.compile(r'["\']X-API-KEY["\']\s*:\s*["\'][^"\']+["\']'),re.compile(r'X[-_]API[-_]KEY\s*=\s*[^ \n]+', re.IGNORECASE),re.compile(r'password\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
]
 
def redact_secrets(text: str) -> str:
    for pat in SECRET_PATTERNS:
        text = pat.sub("[REDACTED]", text)
    return text
 
def should_ignore(path: Path) -> bool:
    if path.resolve() == PATH:
        return True
    name = path.name
    for pattern in IGNORE_PATTERNS:
        pat = pattern.rstrip('/')
        if any(c in pat for c in "*?[]"):
            if fnmatch.fnmatch(name, pat):
                return True
        else:
            if name == pat:
                return True
    return False
 
def is_binary(path: Path, chunk_size: int = 1024) -> bool:
    try:
        with path.open('rb') as f:
            chunk = f.read(chunk_size)
        return b'\0' in chunk
    except OSError:
        return True
 
class FileSystemNode:
    def __init__(self, path: Path, name: str, node_type: str, depth: int = 0):
        self.path = path
        self.name = name
        self.type = node_type
        self.depth = depth
        self.children = []
 
def build_tree(node: FileSystemNode, stats: dict):
    if node.type != "directory":
        return
    try:
        entries = sorted(node.path.iterdir(), key=lambda p: p.name.lower())
    except OSError:
        return
    for entry in entries:
        if should_ignore(entry):
            continue
        if entry.is_symlink():
            link_target = os.readlink(entry)
            child = FileSystemNode(entry, f"{entry.name} -> {link_target}", "symlink", node.depth + 1)
            node.children.append(child)
            stats['files'] += 1
        elif entry.is_dir():
            child = FileSystemNode(entry, entry.name + "/", "directory", node.depth + 1)
            build_tree(child, stats)
            if child.children:
                node.children.append(child)
        elif entry.is_file():
            child = FileSystemNode(entry, entry.name, "file", node.depth + 1)
            node.children.append(child)
            stats['files'] += 1
            try:
                stats['size'] += entry.stat().st_size
            except OSError:
                pass
 
def sort_children(node: FileSystemNode):
    if node.type != "directory":
        return
    def key(child):
        name = child.name.lower()
        if child.type == "file":
            if name.startswith("readme"):
                return (0, name)
            return (1, name)
        if child.type == "directory":
            return (2, name)
        return (3, name)
    node.children.sort(key=key)
    for child in node.children:
        sort_children(child)
 
def create_tree_str(node: FileSystemNode, prefix: str = "", is_last: bool = True) -> str:
    connector = "└── " if is_last else "├── "
    line = f"{prefix}{connector}{node.name}\n"
    if node.type == "directory" and node.children:
        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(node.children):
            line += create_tree_str(child, new_prefix, i == len(node.children) - 1)
    return line
 
def gather_contents(node: FileSystemNode) -> str:
    if node.type == "file":
        header = f"{SEPARATOR}\nFILE: {node.path}\n{SEPARATOR}\n"
        suffix = node.path.suffix.lower()
        if suffix == ".ipynb":
            try:
                nb = nbformat.read(str(node.path), as_version=4)
                code_blocks = []
                for cell in nb.cells:
                    if cell.cell_type == "code" and cell.source.strip():
                        safe_code = redact_secrets(cell.source.rstrip())
                        code_blocks.append(safe_code)
                if not code_blocks:
                    return header + "[No code cells]\n\n"
                return header + "\n\n".join(code_blocks) + "\n\n"
            except Exception as e:
                return header + f"[Error reading notebook: {e}]\n\n"
        if is_binary(node.path):
            return header + "[Binary file]\n\n"
        try:
            text = node.path.read_text(encoding="utf-8", errors="ignore").rstrip()
        except OSError:
            text = "[Error reading file]"
        return header + redact_secrets(text) + "\n\n"
    if node.type == "directory":
        out = ""
        for child in node.children:
            out += gather_contents(child)
        return out
    return ""
 
def compute_extension_breakdown(node: FileSystemNode):
    breakdown = defaultdict(lambda: {'files': 0, 'loc': 0})
    def _recurse(n: FileSystemNode):
        if n.type == "file":
            ext = n.path.suffix.lower() or '[no ext]'
            breakdown[ext]['files'] += 1
            try:
                with n.path.open('r', encoding='utf-8', errors='ignore') as f:
                    breakdown[ext]['loc'] += sum(1 for _ in f)
            except OSError:
                pass
        elif n.type == "directory":
            for child in n.children:
                _recurse(child)
    _recurse(node)
    return breakdown
 
def format_extension_breakdown(breakdown: dict, top_n: int = 10) -> list[str]:
    if not breakdown:
        return []
    items = sorted(breakdown.items(), key=lambda kv: kv[1]['loc'], reverse=True)
    if top_n and len(items) > top_n:
        top_items = items[:top_n]
        rest = items[top_n:]
        other_files = sum(s['files'] for _, s in rest)
        other_loc = sum(s['loc'] for _, s in rest)
        if other_files > 0:
            items = top_items + [('Other', {'files': other_files, 'loc': other_loc})]
        else:
            items = top_items
    lines = []
    for ext, stats in items:
        file_count = stats['files']
        loc_count = stats['loc']
        file_str = f"{file_count:,} file" if file_count == 1 else f"{file_count:,} files"
        loc_str = f"{loc_count:,} line" if loc_count == 1 else f"{loc_count:,} lines"
        lines.append(f"  {ext}: {file_str} ({loc_str})")
    return lines
 
def ingest_directory(path: Path):
    stats = {'files': 0, 'size': 0}
    root = FileSystemNode(path, path.name + "/", "directory")
    build_tree(root, stats)
    sort_children(root)
    tree_body = create_tree_str(root)
    content_str = gather_contents(root)
    breakdown = compute_extension_breakdown(root)
    breakdown_lines = format_extension_breakdown(breakdown, top_n=10)
    est_tokens = f"{len(content_str) // 4:,}"
    summary_lines = [
        SEPARATOR,
        "Summary",
        SEPARATOR,
        f"Directory : {path.name}",
        f"Files analyzed : {stats['files']}",
        f"Estimated tokens : {est_tokens}",
        "",
        "Files",
        *breakdown_lines,
        "",
    ]
    summary = "\n".join(summary_lines)
    tree_lines = [
        "Tree",
        tree_body.rstrip(),
        "",
    ]
    tree = "\n".join(tree_lines)
    return summary, tree, content_str
 
if __name__ == "__main__":
    target_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    target = Path(target_path).resolve()
 
    if not target.is_dir():
        print(f"Error: The specified path '{target}' is not a directory.", file=sys.stderr)
        sys.exit(1)
 
    print(f"Scanning directory: {target}")
    summary, tree, content = ingest_directory(target)
    output_path = target / "context.txt"
 
    try:
        with output_path.open("w", encoding="utf-8") as f:
            f.write(summary)
            f.write("\n")
            f.write(tree)
            f.write("\n")
            f.write(content)
        print(f"Successfully generated context file at: {output_path}")
    except OSError as e:
        print(f"Error: Failed to write output file: {e}", file=sys.stderr)
        sys.exit(1)
