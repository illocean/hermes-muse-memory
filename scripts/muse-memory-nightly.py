"""Native cron script: no outer agent session, use the configured Hermes model."""
import importlib.util
import json
import sys

import hermes_bootstrap
from agent.plugin_llm import PluginLlm
from hermes_constants import get_hermes_home
from hermes_cli.config import load_config_readonly

settings = load_config_readonly().get("plugins", {})
if "muse-memory" not in settings.get("enabled", []) or "muse-memory" in settings.get("disabled", []):
    print('{"success":true,"no_change":true,"disabled":true}')
    raise SystemExit(0)

plugin = get_hermes_home() / "plugins" / "muse-memory"
spec = importlib.util.spec_from_file_location("muse_memory_worker", plugin / "__init__.py", submodule_search_locations=[str(plugin)])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
print(json.dumps(module.run("dream", PluginLlm(plugin_id="muse-memory")), ensure_ascii=False))
