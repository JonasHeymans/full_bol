<?php
/*
Example Automatic Orders EDC Wholesale
www.one-dc.com
For Questions: Please contact support@edc.nl
*/

// This file can be used for testing the order status update-URL
// You do not need this file anymore when everything is running
$update_url = 'http://www.test.nl/edc_order_status_example.php';

$sample_xml = '<?xml version="1.0" encoding="utf-8"?>
<order>
<ordernumber>WS110414234502</ordernumber>
<own_ordernumber>9393920209</own_ordernumber>
<tracktrace>1Z57W468DL53020674</tracktrace>
<shipper>UPS</shipper>
<status>shipped</status>
</order>';

// Send the request
$postfields = 'data='.$sample_xml;
$ch = curl_init($update_url);
curl_setopt($ch,CURLOPT_HEADER,0);
curl_setopt($ch,CURLOPT_POST,1);
curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
curl_setopt($ch,CURLOPT_POSTFIELDS,$postfields);
$result = curl_exec($ch);
curl_close($ch);

echo $result;
?>