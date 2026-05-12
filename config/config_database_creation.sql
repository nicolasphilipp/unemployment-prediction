CREATE TABLE IF NOT EXISTS `district` (
	`district_id` INTEGER UNSIGNED NOT NULL AUTO_INCREMENT,
	`nuts_code` VARCHAR(5) NOT NULL,
	`district_code` INTEGER NOT NULL UNIQUE,
	PRIMARY KEY(`district_id`)
);


CREATE TABLE IF NOT EXISTS `unemployment` (
	`measurement_id` INTEGER NOT NULL,
	`gender` ENUM('Male', 'Female', 'Both') NOT NULL,
	`value` INTEGER NOT NULL,
	`density` DECIMAL NOT NULL,
	PRIMARY KEY(`measurement_id`, `gender`)
);


CREATE TABLE IF NOT EXISTS `measurement_info` (
	`district_id` INTEGER NOT NULL,
	`reference_date` DATE NOT NULL,
	`measurement_id` INTEGER NOT NULL UNIQUE,
	PRIMARY KEY(`district_id`, `reference_date`)
);


CREATE TABLE IF NOT EXISTS `tourism` (
	`mesuremnt_id` INTEGER NOT NULL,
	`value` INTEGER NOT NULL,
	`density` DECIMAL NOT NULL,
	PRIMARY KEY(`mesuremnt_id`)
);


ALTER TABLE `measurement_info`
ADD FOREIGN KEY(`district_id`) REFERENCES `district`(`district_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `unemployment`
ADD FOREIGN KEY(`measurement_id`) REFERENCES `measurement_info`(`measurement_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `tourism`
ADD FOREIGN KEY(`mesuremnt_id`) REFERENCES `measurement_info`(`measurement_id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;