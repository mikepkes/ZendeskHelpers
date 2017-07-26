#!/usr/bin/python
# encoding: utf-8

import os
import string
import sys
import workflow
import tempfile
import subprocess

def getAppleScript(browser="Google Chrome"):
    template = """
        on run argv
            tell application "%s"
            set result to execute front window's active tab javascript "
                attachments = this.document.getElementsByClassName(\\"attachment\\");
                var thisPageAttachments = [];
                for (var i=0; i < attachments.length; i++){
                    thisPageAttachments.push(attachments[i].href);
                }
                thisPageAttachments"
            end tell
            return result
        end run
    """
    
    return template % (browser)

def main(wf):
    
    log = wf.logger
    
    applescript = tempfile.NamedTemporaryFile(suffix=".applescript", delete=False)
    applescript.write(getAppleScript())
    proc = subprocess.Popen(['/usr/bin/osascript', applescript.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    out = None
    err = None
    

    log.debug(out)
    log.debug(err)
    log.debug(applescript.name)
    log.debug("Done!")
    
    wf.add_item(
        title="result",
        arg=out,
        valid=True
    )
    print "test"
    wf.send_feedback()


if __name__ == u"__main__":
    wf = workflow.Workflow(
    #        update_settings={
    #            'github_slug': 'mikepkes/ZendeskHelpers',
    #            'frequency': 1
    #            }
    )
    wf.run(main)