-- --------------------------------------------------------
-- 호스트:                          127.0.0.1
-- 서버 버전:                        8.0.27 - MySQL Community Server - GPL
-- 서버 OS:                        Win64
-- HeidiSQL 버전:                  11.3.0.6295
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- banksystem 데이터베이스 구조 내보내기
CREATE DATABASE IF NOT EXISTS `banksystem` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `banksystem`;

-- 테이블 banksystem.account 구조 내보내기
CREATE TABLE IF NOT EXISTS `account` (
  `acc_number` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '',
  `u_id` int NOT NULL,
  `password` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `acc_type` enum('DEPOSIT','INSTALLMENT','SAVING') DEFAULT 'DEPOSIT',
  `balance` int DEFAULT '0',
  `acc_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `validity` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`acc_number`),
  KEY `FK_us_account` (`u_id`),
  CONSTRAINT `FK_us_account` FOREIGN KEY (`u_id`) REFERENCES `user` (`u_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 내보낼 데이터가 선택되어 있지 않습니다.

-- 테이블 banksystem.bank 구조 내보내기
CREATE TABLE IF NOT EXISTS `bank` (
  `branch_id` int NOT NULL AUTO_INCREMENT,
  `bank_code` char(5) DEFAULT NULL,
  `branch_name` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `location` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`branch_id`),
  UNIQUE KEY `bank_code_branch_name` (`bank_code`,`branch_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 내보낼 데이터가 선택되어 있지 않습니다.

-- 테이블 banksystem.bank_on 구조 내보내기
CREATE TABLE IF NOT EXISTS `bank_on` (
  `manager_id` int NOT NULL,
  `branch_id` int NOT NULL,
  PRIMARY KEY (`manager_id`,`branch_id`),
  KEY `FK_bo_bank` (`branch_id`),
  CONSTRAINT `FK_bo_bank` FOREIGN KEY (`branch_id`) REFERENCES `bank` (`branch_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_bo_manager` FOREIGN KEY (`manager_id`) REFERENCES `manager` (`manager_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 내보낼 데이터가 선택되어 있지 않습니다.

-- 함수 banksystem.check_can_make_account 구조 내보내기
DELIMITER //
CREATE FUNCTION `check_can_make_account`(uid INT) RETURNS int
BEGIN
	DECLARE num INT;
	SELECT COUNT(*) INTO num
	FROM banksystem.user
	WHERE u_id=uid AND
	(
	TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) >= 19 OR
	(TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) < 19 AND protector_id IS NOT NULL)
	);

	RETURN num;
END//
DELIMITER ;

-- 테이블 banksystem.manager 구조 내보내기
CREATE TABLE IF NOT EXISTS `manager` (
  `manager_id` int NOT NULL AUTO_INCREMENT,
  `manager_ssn` varchar(30) NOT NULL,
  `name` varchar(15) DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  PRIMARY KEY (`manager_id`),
  UNIQUE KEY `manager_ssn` (`manager_ssn`)
) ENGINE=InnoDB AUTO_INCREMENT=1005 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 내보낼 데이터가 선택되어 있지 않습니다.

-- 테이블 banksystem.manager_phone 구조 내보내기
CREATE TABLE IF NOT EXISTS `manager_phone` (
  `manager_id` int NOT NULL,
  `phone_number` varchar(20) NOT NULL,
  PRIMARY KEY (`manager_id`,`phone_number`),
  CONSTRAINT `FK_mp_manager` FOREIGN KEY (`manager_id`) REFERENCES `manager` (`manager_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 내보낼 데이터가 선택되어 있지 않습니다.

-- 테이블 banksystem.managing_account 구조 내보내기
CREATE TABLE IF NOT EXISTS `managing_account` (
  `managing_id` int NOT NULL AUTO_INCREMENT,
  `manager_id` int DEFAULT NULL,
  `acc_number` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `command` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `result` char(7) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`managing_id`),
  KEY `FK_mac_acc_number` (`acc_number`),
  KEY `FK_mac_manager` (`manager_id`),
  CONSTRAINT `FK_mac_acc_number` FOREIGN KEY (`acc_number`) REFERENCES `account` (`acc_number`) ON DELETE SET NULL ON UPDATE SET NULL,
  CONSTRAINT `FK_mac_manager` FOREIGN KEY (`manager_id`) REFERENCES `manager` (`manager_id`) ON DELETE SET NULL ON UPDATE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 내보낼 데이터가 선택되어 있지 않습니다.

-- 테이블 banksystem.transaction 구조 내보내기
CREATE TABLE IF NOT EXISTS `transaction` (
  `transaction_id` int NOT NULL AUTO_INCREMENT,
  `acc_number` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `branch_id` int DEFAULT NULL,
  `price` int NOT NULL DEFAULT '0',
  `result` char(7) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT 'FAILED',
  `date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`transaction_id`),
  KEY `FK_tr_bank` (`branch_id`),
  KEY `FK_tr_user` (`acc_number`) USING BTREE,
  CONSTRAINT `FK_tr_account` FOREIGN KEY (`acc_number`) REFERENCES `account` (`acc_number`),
  CONSTRAINT `FK_tr_bank` FOREIGN KEY (`branch_id`) REFERENCES `bank` (`branch_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 내보낼 데이터가 선택되어 있지 않습니다.

-- 테이블 banksystem.transfer 구조 내보내기
CREATE TABLE IF NOT EXISTS `transfer` (
  `transfer_id` int NOT NULL AUTO_INCREMENT,
  `acc_number_from` char(36) DEFAULT NULL,
  `acc_number_to` char(36) DEFAULT NULL,
  `price` int unsigned DEFAULT '0',
  `result` char(7) DEFAULT 'FAILED',
  `date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`transfer_id`),
  KEY `FK_transfer_account` (`acc_number_from`),
  KEY `FK_transfer_account_2` (`acc_number_to`),
  CONSTRAINT `FK_transfer_account` FOREIGN KEY (`acc_number_from`) REFERENCES `account` (`acc_number`) ON DELETE SET NULL ON UPDATE SET NULL,
  CONSTRAINT `FK_transfer_account_2` FOREIGN KEY (`acc_number_to`) REFERENCES `account` (`acc_number`) ON DELETE SET NULL ON UPDATE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 내보낼 데이터가 선택되어 있지 않습니다.

-- 테이블 banksystem.user 구조 내보내기
CREATE TABLE IF NOT EXISTS `user` (
  `u_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `Ssn` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `location` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `birth_date` datetime NOT NULL,
  `credit` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'A',
  `protector_id` int DEFAULT NULL,
  PRIMARY KEY (`u_id`),
  UNIQUE KEY `Ssn` (`Ssn`),
  KEY `FK_us_user` (`protector_id`),
  CONSTRAINT `FK_us_user` FOREIGN KEY (`protector_id`) REFERENCES `user` (`u_id`) ON DELETE SET NULL ON UPDATE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 내보낼 데이터가 선택되어 있지 않습니다.

-- 테이블 banksystem.user_phone 구조 내보내기
CREATE TABLE IF NOT EXISTS `user_phone` (
  `u_id` int NOT NULL,
  `phone_number` varchar(20) NOT NULL,
  PRIMARY KEY (`u_id`,`phone_number`),
  CONSTRAINT `FK_us_user_phone` FOREIGN KEY (`u_id`) REFERENCES `user` (`u_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 내보낼 데이터가 선택되어 있지 않습니다.

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
