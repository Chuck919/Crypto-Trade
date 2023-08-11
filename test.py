from binance.client import Client

key = '0pUTLnduWm1Xe6zkrd6HZ6sZgOWK7iakzmC6dZ7TD4KlJzcAfZo8fIbTE1nRS16d'
secret = 'EihTLWHNdxYcQT0rGXcKW6r3mk2eiH8qQUPUXTjUGzRXCE8RNiMPVqn4NClYYLHb'
client = Client (key, secret, tld='us')

print(client.get_account())