from ai_vps_agent.periodic_monitoring import AgentServer
from ai_vps_agent.server_access.models import SshServerAccess


def test_agent_server_accepts_optional_ssh_access() -> None:
    server = AgentServer(
        id="srv-ssh",
        name="ssh-server",
        hostname="ssh-server.local",
        status="active",
        monitoring_profiles=["profile-linux-baseline"],
        ssh=SshServerAccess(host="127.0.0.1", username="root", private_key_path="C:/keys/id_rsa"),
    )

    assert server.ssh is not None
    assert server.ssh.host == "127.0.0.1"
    assert server.ssh.port == 22
