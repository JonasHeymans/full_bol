<?php
/*
Example Automatic Orders EDC Wholesale
www.one-dc.com
For Questions: Please contact support@edc.nl
*/

// The URL of this file needs to be added as "update URL". Go to "Edit details" on the EDC Shop

// Check if it is a post request
if($_SERVER['REQUEST_METHOD'] == 'POST' && !empty($_POST['data'])){

	// Check if XML functions are installed
	if(!function_exists('xml_parser_create')){
		die('You do not have the XML Parser functions installed! Ask your host for more info.');
	} else {
	
		// Load the XML feed
		$p = xml_parser_create();
		xml_parse_into_struct($p,$_POST['data'],$vals,$index);
		xml_parser_free($p);

		// Find the index keys
		$ordernumber_index = $index['ORDERNUMBER'][0];
		$own_ordernumber_index = $index['OWN_ORDERNUMBER'][0];
		$new_ordernumber_index = $index['NEW_ORDERNUMBER'][0];
		$trackingnumber_index = $index['TRACKTRACE'][0];
		$shipper_index = $index['SHIPPER'][0];
		$amount_index = $index['AMOUNT'][0];

		// Find the values
		$ordernumber = $vals[$ordernumber_index]['value'];
		$own_ordernumber = $vals[$own_ordernumber_index]['value'];
		$new_ordernumber = $vals[$new_ordernumber_index]['value'];
		$trackingnumber = $vals[$trackingnumber_index]['value'];
		$shipper = $vals[$shipper_index]['value'];
		$amount = $vals[$amount_index]['value'];

		// Output
		// Check whether a backorder has been created
		if(!empty($new_ordernumber)){
			echo 'A backorder has been created for '.$ordernumber.'. The new order number is: '.$new_ordernumber;
		} else {
			echo '<p>
			Ordernumber EDC: '.$ordernumber.'<br />
			Own Ordernumber: '.$own_ordernumber.'<br />
			Shipper: '.$shipper.'<br />
			Tracking number: '.$trackingnumber.'<br />
			Total amount incl. VAT: '.$amount.' EUR</p>';
		}
	

	}	
}
?>