import os, shutil, subprocess, re, time, jinja2
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
load_dotenv()

GODOT_PATH = os.environ["GODOT_PATH"]
STEAMCMD_PATH = os.environ["STEAMCMD_PATH"]
STEAM_USERNAME = os.environ["STEAM_USERNAME"]
PROJECT_PATH = os.environ["PROJECT_PATH"]
PROJECT_NAME = os.environ["PROJECT_NAME"]
APPID = os.environ["APPID"]
CONTENT_DEPOT_ID = os.environ["CONTENT_DEPOT_ID"]
WINDOWS_DEPOT_ID = os.environ["WINDOWS_DEPOT_ID"]
MACOS_DEPOT_ID = os.environ["MACOS_DEPOT_ID"]
LINUX_DEPOT_ID = os.environ["LINUX_DEPOT_ID"]
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

def clean(path: str):
	shutil.rmtree(path, ignore_errors=True)
	os.makedirs(path)

def export(full_name: str, name_code: str, extension: str):
	exe_path = os.path.abspath("{}/{}.{}".format(name_code, PROJECT_NAME, extension))
	print("Executable: {}".format(exe_path))

	# Export
	subprocess.call([
		GODOT_PATH,
		"--headless",
		"--path",
		PROJECT_PATH,
		"--export-release",
		full_name,
		exe_path
	]) 

def package(source_dir: str, zip_name: str):
	print("Packing {} to {}...".format(source_dir, zip_name))
	shutil.make_archive(zip_name, "zip", source_dir)

def steam_login():
	subprocess.call([
		STEAMCMD_PATH,
		"+login",
		STEAM_USERNAME
	])

def get_steam_script_jinja_context() -> dict[str, str]:
	return {
		"appid": APPID,
		"content_depot_id": CONTENT_DEPOT_ID,
		"windows_depot_id": WINDOWS_DEPOT_ID,
		"macos_depot_id": MACOS_DEPOT_ID,
		"linux_depot_id": LINUX_DEPOT_ID
	}

def generate_steam_scripts():
	env = jinja2.Environment(
		loader=jinja2.FileSystemLoader("steam_script_templates"),
		autoescape=jinja2.select_autoescape()
	)

	clean("steam_scripts")

	for template_name in env.list_templates():
		template = env.get_template(template_name)
		rendered_script: str = template.render(get_steam_script_jinja_context())

		output_name = template_name.replace(".j2", "")
		rendered_file = open("steam_scripts/" + output_name, "w")
		rendered_file.write(rendered_script)

def run_steam_script(path: str):
	subprocess.call([
		STEAMCMD_PATH,
		"+run_app_build",
		path
	])

def upload_all_depots_to_steam():
	generate_steam_scripts()

	subprocess.call([
		STEAMCMD_PATH,
		"+login", STEAM_USERNAME,
		"+run_app_build", os.path.abspath("./steam_scripts/upload_content.vdf"),
		"+run_app_build", os.path.abspath("./steam_scripts/upload_win.vdf"),
		# "+run_app_build", os.path.abspath("./steam_scripts/upload_macos.vdf"), TODO
		"+run_app_build", os.path.abspath("./steam_scripts/upload_linux.vdf"),
		"+exit"
	])

def upload_content_to_steam():
	generate_steam_scripts()
	
	subprocess.call([
		STEAMCMD_PATH,
		"+login", STEAM_USERNAME,
		"+run_app_build", os.path.abspath("./steam_scripts/upload_content.vdf"),
		"+exit"
	])

def update_version():
	new_version = input("New version: ")
	
	# Modify project file
	proj_file = open(os.path.join(PROJECT_PATH, "project.godot"), "r")
	proj_text = proj_file.read()
	proj_file.close()

	proj_text = re.sub(r"config/version=\"(.*)\"", "config/version=\"{}\"".format(new_version), proj_text)

	proj_file = open(os.path.join(PROJECT_PATH, "project.godot"), "w")
	proj_file.write(proj_text)
	proj_file.close()

	return new_version

def clean_all():
	clean("win")
	clean("macos")
	clean("linux")

def export_all():
	clean_all()	

	export("Windows", "win", "exe")
	export("macOS", "macos", "app")
	export("Linux", "linux", "x86_64")

def package_all(version: str):
	export_all()

	package("win", "{}_{}_win".format(PROJECT_NAME, version))
	package("macos", "{}_{}_macos".format(PROJECT_NAME, version))
	package("linux", "{}_{}_linux".format(PROJECT_NAME, version))

def post_slack_message(message: str):
	if not SLACK_TOKEN or not SLACK_CHANNEL_ID:
		return # Don't send a message if there's no Slack config.

	client = WebClient(token=SLACK_TOKEN)
	try:
		
		client.chat_postMessage( # type: ignore
			channel=SLACK_CHANNEL_ID,
			markdown_text=message
		)
	except SlackApiError as e:
		print(e)

def main():
	print("Project path: {}".format(PROJECT_PATH))
	print()

	new_version = update_version()

	start = time.time()

	package_all(new_version)

	end = time.time()

	print()
	print()

	print("Exporting and packaging took {}s.".format(end - start))

	print()

	if input("Upload content only (Y/n)? ").lower().startswith("n"):
		upload_all_depots_to_steam()
	else:
		upload_content_to_steam()

	post_slack_message(":tada::godot: Created and uploaded version *{}* to Steam.\nMake sure to mark the build as latest in the Steamworks API to make it public.".format(new_version))

if __name__ == "__main__":
	main()
