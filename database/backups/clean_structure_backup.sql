CREATE TABLE `buyers` (
  `user_id` int NOT NULL,
  `buyer_number` int NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`buyer_number`),
  UNIQUE KEY `uk_buyer_name_phone_user` (`user_id`,`name`,`phone`),
  KEY `fk_buyers_user_idx` (`user_id`),
  CONSTRAINT `fk_buyers_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    DECLARE next_number INT DEFAULT 1;

    
    SELECT COALESCE(MAX(buyer_number), 0) + 1 INTO next_number
    FROM buyers
    WHERE user_id = NEW.user_id;

    SET NEW.buyer_number = next_number;
END */;;
CREATE TABLE `projects` (
  `user_id` int NOT NULL,
  `project_number` int NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`project_number`),
  KEY `fk_projects_user_idx` (`user_id`),
  KEY `idx_user_name` (`user_id`,`name`),
  CONSTRAINT `fk_projects_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    DECLARE next_number INT DEFAULT 1;

    
    SELECT COALESCE(MAX(project_number), 0) + 1 INTO next_number
    FROM projects
    WHERE user_id = NEW.user_id;

    SET NEW.project_number = next_number;
END */;;
CREATE TABLE `raffle_sets` (
  `user_id` int NOT NULL,
  `project_number` int NOT NULL,
  `set_number` int NOT NULL,
  `name` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` enum('online','physical') COLLATE utf8mb4_unicode_ci NOT NULL,
  `init` int NOT NULL,
  `final` int NOT NULL,
  `unit_price` int NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`project_number`,`set_number`),
  KEY `fk_raffle_sets_user_idx` (`user_id`),
  KEY `fk_raffle_sets_project_idx` (`user_id`,`project_number`),
  CONSTRAINT `fk_raffle_sets_project` FOREIGN KEY (`user_id`, `project_number`) REFERENCES `projects` (`user_id`, `project_number`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_raffle_sets_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_valid_numbers` CHECK ((`init` <= `final`)),
  CONSTRAINT `chk_valid_type` CHECK ((`type` in (_utf8mb3'online',_utf8mb3'physical')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    DECLARE next_number INT DEFAULT 1;

    
    SELECT COALESCE(MAX(set_number), 0) + 1 INTO next_number
    FROM raffle_sets
    WHERE user_id = NEW.user_id AND project_number = NEW.project_number;

    SET NEW.set_number = next_number;
END */;;
CREATE TABLE `raffles` (
  `user_id` int NOT NULL,
  `project_number` int NOT NULL,
  `raffle_number` int NOT NULL,
  `set_number` int NOT NULL,
  `buyer_user_id` int DEFAULT NULL,
  `buyer_number` int DEFAULT NULL,
  `payment_method` enum('cash','card','transfer') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `state` enum('available','sold','reserved') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'available',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`project_number`,`raffle_number`),
  KEY `fk_raffles_user_idx` (`user_id`),
  KEY `fk_raffles_project_idx` (`user_id`,`project_number`),
  KEY `fk_raffles_raffle_set_idx` (`user_id`,`project_number`,`set_number`),
  KEY `fk_raffles_buyer_idx` (`buyer_user_id`,`buyer_number`),
  KEY `idx_state` (`state`),
  KEY `idx_payment_method` (`payment_method`),
  CONSTRAINT `fk_raffles_buyer` FOREIGN KEY (`buyer_user_id`, `buyer_number`) REFERENCES `buyers` (`user_id`, `buyer_number`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_raffles_raffle_set` FOREIGN KEY (`user_id`, `project_number`, `set_number`) REFERENCES `raffle_sets` (`user_id`, `project_number`, `set_number`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_raffles_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    DECLARE next_number INT DEFAULT 1;

    
    SELECT COALESCE(MAX(raffle_number), 0) + 1 INTO next_number
    FROM raffles
    WHERE user_id = NEW.user_id AND project_number = NEW.project_number;

    SET NEW.raffle_number = next_number;
END */;;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `hashed_password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  KEY `idx_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
