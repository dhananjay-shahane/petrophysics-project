  GNU nano 7.2                                            start.sh                                                      #!/bin/bash
export NVM_DIR="/root/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
cd /root/deploy/petrophysics-project
npm run dev