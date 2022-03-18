-- phpMyAdmin SQL Dump
-- version 4.4.15.10
-- https://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Mar 18, 2022 at 10:58 PM
-- Server version: 5.5.68-MariaDB
-- PHP Version: 5.4.16

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `domain_proxy`
--

-- --------------------------------------------------------

--
-- Table structure for table `cbsd`
--

CREATE TABLE IF NOT EXISTS `cbsd` (
  `id` int(11) NOT NULL,
  `state_id` int(11) NOT NULL,
  `user_id` varchar(30) DEFAULT NULL,
  `fcc_id` varchar(30) DEFAULT NULL,
  `cbsd_id` varchar(255) DEFAULT NULL,
  `cbsd_category` char(1) DEFAULT NULL,
  `cbsd_serial_number` varchar(30) DEFAULT NULL,
  `cbsd_action` varchar(20) DEFAULT NULL,
  `time_updated` datetime DEFAULT NULL
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `cbsd`
--

INSERT INTO `cbsd` (`id`, `state_id`, `user_id`, `fcc_id`, `cbsd_id`, `cbsd_category`, `cbsd_serial_number`, `cbsd_action`, `time_updated`) VALUES
(1, 2, 'Test-inc', '2AQ68T99B226', '2AQ68T99B226Mock-SAS900F0C732A03', 'B', '900F0C732A03', 'deregister', '2022-03-17 17:51:19'),
(2, 2, 'Test-inc', '2AQ68T99B226', '2AQ68T99B226Mock-SAS900F0C732A02', 'B', '900F0C732A02', 'deregister', '2022-03-17 17:51:19');

-- --------------------------------------------------------

--
-- Table structure for table `cbsd_state`
--

CREATE TABLE IF NOT EXISTS `cbsd_state` (
  `id` int(11) NOT NULL,
  `name` varchar(20) NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `cbsd_state`
--

INSERT INTO `cbsd_state` (`id`, `name`) VALUES
(2, 'DEREGISTERED'),
(1, 'REGISTERED');

-- --------------------------------------------------------

--
-- Table structure for table `device_info`
--

CREATE TABLE IF NOT EXISTS `device_info` (
  `userID` varchar(50) NOT NULL,
  `fccID` varchar(50) NOT NULL,
  `SN` varchar(50) NOT NULL,
  `cbsdID` varchar(50) NOT NULL,
  `cbsdCategory` varchar(1) NOT NULL,
  `maxEIRP` int(11) NOT NULL,
  `lowFrequency` int(11) NOT NULL,
  `highFrequency` int(11) NOT NULL,
  `sasStage` varchar(50) NOT NULL,
  `TxPower` int(11) NOT NULL,
  `EARFCN` varchar(20) NOT NULL,
  `antennaGain` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `device_info`
--

INSERT INTO `device_info` (`userID`, `fccID`, `SN`, `cbsdID`, `cbsdCategory`, `maxEIRP`, `lowFrequency`, `highFrequency`, `sasStage`, `TxPower`, `EARFCN`, `antennaGain`) VALUES
('Robert Smith', 'abc123', '1111', 'abc123Mock-SAS1111', 'B', 0, 3550, 3570, 'heartbeat', 20, '55240', 2),
('Robert Smith', 'cde456', '2222', 'cde456Mock-SAS2222', 'B', 0, 0, 0, 'notused', 0, '', 0),
('Robert Smith', 'fgh789', '3333', 'fgh789Mock-SAS3333', 'B', 0, 0, 0, 'notused', 0, '', 0),
('Robert Smith', 'xyz123', '4444', 'xyz123Mock-SAS4444', 'B', 0, 3670, 3700, 'heartbeat', 20, '56739', 2);

-- --------------------------------------------------------

--
-- Table structure for table `heartbeat`
--

CREATE TABLE IF NOT EXISTS `heartbeat` (
  `cbsdID` varchar(50) NOT NULL,
  `grantID` varchar(50) NOT NULL,
  `renewGrant` tinyint(1) NOT NULL,
  `measReport` tinyint(1) NOT NULL,
  `opParams` tinyint(1) DEFAULT NULL,
  `operationalState` varchar(10) NOT NULL,
  `transmitExpireTime` datetime NOT NULL,
  `grantExpireTime` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `heartbeat`
--

INSERT INTO `heartbeat` (`cbsdID`, `grantID`, `renewGrant`, `measReport`, `opParams`, `operationalState`, `transmitExpireTime`, `grantExpireTime`) VALUES
('abc123Mock-SAS1111', '557102236', 0, 0, NULL, 'AUTHORIZED', '2021-03-30 17:23:52', '2021-04-06 17:20:08'),
('xyz123Mock-SAS4444', '393375046', 0, 0, NULL, 'AUTHORIZED', '2021-03-30 17:23:52', '2021-04-06 17:20:08');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `cbsd`
--
ALTER TABLE `cbsd`
  ADD PRIMARY KEY (`id`),
  ADD KEY `state_id` (`state_id`);

--
-- Indexes for table `cbsd_state`
--
ALTER TABLE `cbsd_state`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `device_info`
--
ALTER TABLE `device_info`
  ADD PRIMARY KEY (`SN`);

--
-- Indexes for table `heartbeat`
--
ALTER TABLE `heartbeat`
  ADD PRIMARY KEY (`cbsdID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `cbsd`
--
ALTER TABLE `cbsd`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=5;
--
-- AUTO_INCREMENT for table `cbsd_state`
--
ALTER TABLE `cbsd_state`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=3;
--
-- Constraints for dumped tables
--

--
-- Constraints for table `cbsd`
--
ALTER TABLE `cbsd`
  ADD CONSTRAINT `cbsd_ibfk_1` FOREIGN KEY (`state_id`) REFERENCES `cbsd_state` (`id`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
