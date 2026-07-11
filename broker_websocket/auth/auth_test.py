from broker_websocket.auth.auth import auth

print("=" * 60)
print("AUTH TEST")
print("=" * 60)


session = auth.get_session()
print(session)