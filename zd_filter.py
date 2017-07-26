#!/usr/bin/python
# encoding: utf-8

import os
import string
import sys
import workflow
import tempfile
import subprocess
import urlparse
import md5
from workflow.background import is_running, run_in_background


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
    
    applescript = tempfile.NamedTemporaryFile(suffix=".applescript", delete=True)
    applescript.write(getAppleScript())
    applescript.flush()
    proc = subprocess.Popen(['/usr/bin/osascript', applescript.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = proc.communicate()

    attachments = out.split(", ")
    
    cache_dir = wf.alfred_env['workflow_cache']

    for attachment in attachments:
        try:
            qs = urlparse.urlparse(attachment).query
            (qsKey, qsValue) = qs.split('=')
            if qsKey == 'name':
                name = qsValue
            else:
                name = attachment
                
            digest = md5.md5(attachment).hexdigest()
            cached_image_path = os.path.join(cache_dir, digest)
            wf.add_item(
                title=name,
                subtitle=attachment,
                arg="![%s](%s)" % (name, attachment),
                quicklookurl=attachment,
                valid=True
            )
        except Exception as e:
            log.debug(e)

    wf.send_feedback()


if __name__ == u"__main__":
    wf = workflow.Workflow(
            update_settings={
                'github_slug': 'mikepkes/ZendeskHelpers',
                'frequency': 1
                }
    )
    if wf.update_available:
        # Download new version and tell Alfred to install it
        wf.start_update()
    
    wf.run(main)
