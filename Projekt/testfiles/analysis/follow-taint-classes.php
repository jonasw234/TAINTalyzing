<?php
class FollowMe
{
    public function evalVuln($test='')
    {
        eval($test);
    }
}

class TaintedByProxy
{
    public function proxyTaint($test='')
    {
        $follow = new FollowMe();
        $follow->evalVuln($test);
    }
}

?>
