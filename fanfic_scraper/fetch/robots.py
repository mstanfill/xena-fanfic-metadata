from dataclasses import dataclass


@dataclass
class RobotsRules:
    disallow_prefixes: list
    crawl_delay: float | None = None

    def is_allowed(self, path: str) -> bool:
        return not any(prefix and path.startswith(prefix) for prefix in self.disallow_prefixes)


def parse_robots(text: str, user_agent_token: str = "*") -> RobotsRules:
    groups = []  # list[(agents: list[str], directives: list[(key, value)])]
    current_agents, current_directives, started_directives = [], [], False

    def flush():
        if current_agents:
            groups.append((list(current_agents), list(current_directives)))

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip().lower(), value.strip()
        if key == "user-agent":
            if started_directives:
                flush()
                current_agents, current_directives, started_directives = [], [], False
            current_agents.append(value)
        elif key in ("disallow", "crawl-delay"):
            started_directives = True
            current_directives.append((key, value))
    flush()

    directives = []
    for agents, dirs in groups:
        if user_agent_token in agents:
            directives = dirs
            break
    else:
        for agents, dirs in groups:
            if "*" in agents:
                directives = dirs
                break

    disallow = [v for k, v in directives if k == "disallow" and v]
    crawl_delay = None
    for k, v in directives:
        if k == "crawl-delay":
            try:
                crawl_delay = float(v)
            except ValueError:
                pass
    return RobotsRules(disallow_prefixes=disallow, crawl_delay=crawl_delay)
