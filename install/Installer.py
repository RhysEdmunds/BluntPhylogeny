

"""
Sets the environment to run the pasta docker -- perhaps this should be in install...

Checks whether Docker is present on the system
    - if not, asks whether it can install Docker (Is there a Docker lite for just one image?)

Checks whether smirarab/pasta is inlcuded as an image
    - if not, includes it
    
Checks whether Docker has its databases linked
    - if not, links it
"""

def set_pasta_env():
    pasta_sh_lines = []
    
    log("Checking docker exists")
    from shutil import which
    client_exists = (False if which("Docker") is None else True)

    if not client_exists and Settings['can_install'] > 0:
        # TODO: can_install = ask_everytime # TODO: ENUM
        
        log("\tInstalling docker")
        
        # TODO: pulling Docker Desktop installer?
        p = Popen("\"Docker Desktop Installer.exe\" install", stdout=PIPE)
        for line in TextIOWrapper(p.stdout):
            log("\t", line.rstrip())

    elif not client_exists and Settings['can_install'] == 0:
        log("Error: Cannot install Docker due to Settings")
        return False

    # Getting the docker from the environment
    client = docker.from_env()
    
    log("Checking whether smirarab/pasta exists")
    if not 'smirarab/pasta' in client.images.list():
        # Pulling pasta alignment image
        log("Pulling smirarab/pasta")
        client.images.pull("smirarab/pasta")

    # Making sure the -v works:
    # docker run -v [path to the directory with your input files]:/data smirarab/pasta run_pasta.py -i input_fasta [-t starting_tree] 
    log("Checking docker volume links correctly")
    # TODO

    return True

""" UNIT TEST -- Perhaps this piece of code should be in set-up
--- 1 ---
env: Settings['can install']==0;docker abscent
result: return False
--- 2 ---
env: Settings['can install']==1;docker abscent
result: install docker;install smirarab;return True
--- 3 ---
env: Settings['can install']==0;docker present; smirarab abscent
result: install smirarab; return True
--- 4 ---
env: Settings['can install']==1;docker present;smirarab present
result: return True
"""