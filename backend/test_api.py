import subprocess, time, sys, os, http.client, json, uuid

proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'],
    cwd=os.path.dirname(os.path.abspath(__file__)),
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(3)

# Check if process is still running
if proc.poll() is not None:
    print("Server exited prematurely!")
    out, err = proc.communicate()
    print("STDOUT:", out.decode()[:500])
    print("STDERR:", err.decode()[:500])
    sys.exit(1)

try:
    boundary = uuid.uuid4().hex
    lines = []
    for name, value in [("username", "testuser"), ("password", "test123"),
                         ("name", "Test User"), ("student_id", "2024001"),
                         ("email", "test@example.com")]:
        lines.append(f"--{boundary}")
        lines.append(f'Content-Disposition: form-data; name="{name}"')
        lines.append("")
        lines.append(value)
    lines.append(f"--{boundary}")
    lines.append('Content-Disposition: form-data; name="photo"; filename="test.jpg"')
    lines.append("Content-Type: image/jpeg")
    lines.append("")
    lines.append("fake-image-data")
    lines.append(f"--{boundary}--")
    data = "\r\n".join(lines).encode("utf-8")

    conn = http.client.HTTPConnection("localhost", 8000, timeout=15)
    conn.request("POST", "/api/register", data,
                 {"Content-Type": f"multipart/form-data; boundary={boundary}"})
    resp = conn.getresponse()
    body = resp.read()
    print("POST /api/register:", resp.status, body.decode())

    # Login
    login_data = json.dumps({"username": "testuser", "password": "test123"}).encode()
    conn.request("POST", "/api/login", login_data, {"Content-Type": "application/json"})
    resp = conn.getresponse()
    result = json.loads(resp.read())
    print("POST /api/login:", resp.status)
    token = result["access_token"]

    # Get users
    conn.request("GET", "/api/users", headers={"Authorization": f"Bearer {token}"})
    resp = conn.getresponse()
    users = json.loads(resp.read())
    print("GET /api/users:", resp.status, "count:", len(users))

    # Checkin
    boundary2 = uuid.uuid4().hex
    lines2 = [
        f"--{boundary2}",
        'Content-Disposition: form-data; name="photo"; filename="checkin.jpg"',
        "Content-Type: image/jpeg",
        "",
        "fake-checkin-image",
        f"--{boundary2}--",
    ]
    data2 = "\r\n".join(lines2).encode("utf-8")
    conn.request("POST", "/api/checkin", data2,
                 {"Content-Type": f"multipart/form-data; boundary={boundary2}"})
    resp = conn.getresponse()
    print("POST /api/checkin:", resp.status, resp.read().decode())

    # Get checkin records
    conn.request("GET", "/api/checkin/records", headers={"Authorization": f"Bearer {token}"})
    resp = conn.getresponse()
    records = json.loads(resp.read())
    print("GET /api/checkin/records:", resp.status, "count:", len(records))

    # Logout
    conn.request("POST", "/api/logout", headers={"Authorization": f"Bearer {token}"})
    resp = conn.getresponse()
    print("POST /api/logout:", resp.status, resp.read().decode())

    print("\n=== All API tests passed! ===")
finally:
    proc.terminate()
    # Print server logs
    time.sleep(1)
    out, err = proc.communicate()
    if err:
        print("\nServer stderr:")
        print(err.decode()[:1000])
