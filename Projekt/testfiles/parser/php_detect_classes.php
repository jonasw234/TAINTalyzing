<?php
class MyClass
{
    public function __construct()
    {
        echo 'The class "', __CLASS__, '" was initiated!<br />';
    }
}

class MyOtherClass extends MyClass
{
    public function newMethod()
    {
        echo "From a new method in " . __CLASS__ . ".<br />";
    }
}

$foo = new MyOtherClass();
$foo->newMethod();
?>
