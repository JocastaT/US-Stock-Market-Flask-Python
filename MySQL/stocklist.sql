-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Feb 24, 2022 at 07:44 PM
-- Server version: 10.4.14-MariaDB
-- PHP Version: 7.2.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `test`
--

-- --------------------------------------------------------

--
-- Table structure for table `stocklist`
--

CREATE TABLE `stocklist` (
  `id` int(11) NOT NULL,
  `symbol` varchar(45) NOT NULL,
  `name` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `stocklist`
--

INSERT INTO `stocklist` (`id`, `symbol`, `name`) VALUES
(1, 'AAPL', 'Apple Inc.'),
(2, 'MSFT', 'Microsoft Corporation'),
(3, 'TSLA', 'Tesla, Inc.'),
(4, 'KO', 'The Coca-Cola Company'),
(5, 'VIAC', 'Paramount Global'),
(6, 'DKNG', 'DraftKings Inc.'),
(7, 'INTC', 'Intel Corporation'),
(8, 'NVDA', 'NVDIA Corporation'),
(9, 'ROKU', 'Roku, Inc'),
(10, 'SOFI', 'SoFi Technologies, Inc.'),
(11, 'RBLX', 'Roblox Corporation'),
(12, 'BAC', 'Bank of America Corporation'),
(13, 'FB', 'Meta Platforms'),
(14, 'CSCO', 'Cisco Systems, Inc'),
(15, 'AAL', 'American Airlines Group Inc.'),
(16, 'UBER', 'Uber Technologies, Inc.'),
(17, 'PYPL', 'PayPal Holdings, Inc.'),
(18, 'NOK', 'Nokia Corporation'),
(19, 'BABA', 'Alibaba Group Holding Limited'),
(20, 'TWTR', 'Twitter, Inc.');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `stocklist`
--
ALTER TABLE `stocklist`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `stocklist`
--
ALTER TABLE `stocklist`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
