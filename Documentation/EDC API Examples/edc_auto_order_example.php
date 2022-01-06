<?php
/*
Example Automatic Orders EDC Wholesale
www.one-dc.com
For Questions: Please contact support@edc.nl
*/

// Configuration
$email = 'testaccount@edc-internet.nl';
$apikey = '7651320RK8RD972HR966Z40752DDKZKK';

// API URL
$apiurl = 'https://www.one-dc.com/ao/';

// Make sure that you put your data (name, street, city etc) in utf8
// use utf8_encode() if your website uses another charset (iso-8859-1 or windows-1252)

// Make the XML
// This example script uses the "advanced" output mode
$xml = '<?xml version="1.0"?>
<orderdetails>
<customerdetails>
	<email>'.$email.'</email>
	<apikey>'.$apikey.'</apikey>
	<output>advanced</output>
</customerdetails>
<receiver>
	<name>Test Person</name>
	<street>Test street</street>
	<house_nr>24</house_nr>
	<postalcode>2628BL</postalcode>
	<city>Test city</city>
	<country></country>
	<phone>+31567234939</phone>
</receiver>
<products>
	<artnr>05633310000</artnr>
</products>
</orderdetails>';

// Check whether the config vars are all set
if(empty($email) || empty($password)){
	die('Please enter your config vars');
}

// Check whether the cURL module has been installed
if(!function_exists('curl_init')){
	die('You do not have the cURL functions installed! Ask your host for more info.');
} else {

	// Send the XML request
	$postfields = 'data='.$xml;
	$ch = curl_init($apiurl);
	curl_setopt($ch,CURLOPT_HEADER,0);
	curl_setopt($ch,CURLOPT_POST,1);
	curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
	curl_setopt($ch,CURLOPT_POSTFIELDS,$postfields);
	$result = curl_exec($ch);
	curl_close($ch);

	if($ch === false || $result === false){
		die('There was a problem with the connection to EDC');
	} else {
		$json = json_decode($result,true);

		// Success
		if($json['result'] == 'OK'){

			echo '<pre>';
			echo 'The order was successful. The following output was received from EDC:'.PHP_EOL;
			print_r($json);
			echo '</pre>';
			
		// Failure
		} else {
			echo '<pre>';
			echo 'There was a problem with the order request. The following output was received from EDC:'.PHP_EOL;
			print_r($json);
			echo '</pre>';
		}
	}
}
?>