# Dev Container

## Setup

Install Docker (Ubuntu)

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

Add yourself to docker users

```bash
sudo usermod -aG docker steven
docker run hello-world
```

Test it

```bash
sudo docker run hello-world
```

Reboot, then test your own user

```bash
sudo reboot now
```

```bash
docker run hello-world
```
