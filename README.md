# The Orchestrator SDK
This submodule is a shared resource that assists python applications to easily leaverage The Orchestrator message broker.

## Capabilities
- Easy creation of event/command publishers and subscribers
- Startup syncronization and version validation to broker
- Local transactional integrity (2PC/OutBox)

## Add to Python Project
1. Create a submodule folder in the root of your python application called 'orchestrator_sdk' (From main) <br/>
`git submodule add https://github.com/Mariustotle/TheOrchestratorSdkPython.git orchestrator_sdk`
2. Add the packages from "requirements.txt" to your main application "requirements.txt"

## How to update the Submodule
Update external (submodules) git repositories to latest remote version
1. Open the root of the submodule in explorer and type CMD in address
2. Run > `Git Pull / git submodule foreach git pull origin master`
3. Commit the changes in the parent repo (Updated commit reference)


