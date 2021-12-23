-- algotrading.assets definition

CREATE TABLE `assets` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `is_native` tinyint(1) NOT NULL DEFAULT 0,
  `token_name` varchar(100) NOT NULL,
  `token_code` varchar(16) NOT NULL,
  `token_asset_id` int(10) unsigned NOT NULL,
  `token_network` varchar(8) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT DEFAULT CHARSET=utf8 COMMENT='Holds information on the native Algo token and ASAs that are supported by the trading bot.';


-- algotrading.trades definition

CREATE TABLE `trades` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `wallet_address` varchar(64) NOT NULL,
  `asset1_id` int(10) unsigned NOT NULL,
  `asset2_id` int(10) unsigned NOT NULL,
  `asset_in_id` int(10) unsigned NOT NULL,
  `asset_in_amt` bigint(20) unsigned NOT NULL,
  `slippage` decimal(6,3) NOT NULL,
  `min_price_for_sell` decimal(8,3) NOT NULL,
  `do_redeem` tinyint(1) NOT NULL DEFAULT 1,
  `is_completed` tinyint(1) NOT NULL DEFAULT 0,
  `do_reverse` tinyint(1) NOT NULL DEFAULT 0,
  `token_network` varchar(8) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `swaps_wanted_FK` (`asset1_id`),
  KEY `swaps_wanted_FK_1` (`asset2_id`),
  KEY `swaps_wanted_FK_2` (`asset_in_id`),
  CONSTRAINT `swaps_wanted_FK` FOREIGN KEY (`asset1_id`) REFERENCES `assets` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `swaps_wanted_FK_1` FOREIGN KEY (`asset2_id`) REFERENCES `assets` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `swaps_wanted_FK_2` FOREIGN KEY (`asset_in_id`) REFERENCES `assets` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT DEFAULT CHARSET=utf8 COMMENT='Holds records of trades that we want to transact and the conditions with which they are allowed, as well as a flag to indicate when the trades are successfully executed.';