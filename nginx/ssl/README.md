# SSL Certificates

Place your TLS certificates here before starting Nginx with HTTPS:

```
nginx/ssl/fullchain.pem
nginx/ssl/privkey.pem
```

## For development (self-signed)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/C=BD/ST=Dhaka/L=Dhaka/O=ISP/CN=localhost"
```

## For production

Use Let's Encrypt (certbot) on the host and copy/symlink the live certs into
this directory, e.g.:

```bash
sudo cp /etc/letsencrypt/live/your-domain/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain/privkey.pem  nginx/ssl/
```

If you do NOT have certificates yet, comment out the `listen 443 ssl http2;`
server block in `nginx/nginx.conf` and use the HTTP-only setup so the stack
will still start.
