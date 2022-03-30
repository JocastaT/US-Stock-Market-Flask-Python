-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Feb 24, 2022 at 07:40 PM
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

-- --------------------------------------------------------

--
-- Table structure for table `stocks`
--

CREATE TABLE `stocks` (
  `id` int(8) NOT NULL,
  `symbol` varchar(45) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `stocksNo` int(11) NOT NULL,
  `marketPrice` varchar(45) NOT NULL,
  `totalAmt` int(11) NOT NULL,
  `date` varchar(45) NOT NULL,
  `user` varchar(45) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `stocks`
--

INSERT INTO `stocks` (`id`, `symbol`, `stocksNo`, `marketPrice`, `totalAmt`, `date`, `user`) VALUES
(3247, 'AAPL', 12, '1', 1200, '02/24/2022, 09:37:19', 'studentC07@email.com'),
(3269, 'SOFI', 12, '9.82', 15908, '02/24/2022, 16:15:19', 'studentC07@email.com'),
(3270, 'ROKU', 2, '118.35', 31954, '02/24/2022, 16:21:23', 'studentC07@email.com'),
(3271, 'ROKU', 2, '118.35', 31954, '02/24/2022, 16:21:30', 'studentC07@email.com'),
(3288, 'BAC', 5, '44.78', 30226, '02/24/2022, 17:49:08', 'studentC07@email.com'),
(3287, 'RBLX', 3, '45.68', 18500, '02/24/2022, 17:43:13', 'studentC07@email.com'),
(3286, 'ROKU', 2, '118.35', 31954, '02/24/2022, 17:36:27', 'studentC07@email.com'),
(3285, 'ROKU', 3, '118.35', 47931, '02/24/2022, 17:21:43', 'studentC07@email.com');

-- --------------------------------------------------------

--
-- Table structure for table `user_flask`
--

CREATE TABLE `user_flask` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(150) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `user_flask`
--

INSERT INTO `user_flask` (`id`, `name`, `email`, `username`, `password`) VALUES
(1, 'jocasta tan', 'jocastatan0171@gmail.com', 'ripthatpuuuuss5', '12345'),
(2, '12', 'studentC07@email.com', 'slutforredhairedgaybitche', '123'),
(3, '1', 'jocastatan0171@gmail.com', 'joc4sta', '$5$rounds=535000$qsRJMWP3L45riEVM$ORaOPOJeZ1JdrvyCk0xKe7FyL6ooty44LB4o5je7gt4'),
(4, 'jocasta tan', 'jocastatan0171@gmail.com', 'ripthatpuuuuss5', '$5$rounds=535000$GxCN2EI8H7jbhZP5$UQiMqNte4QUe8XMZnM.6upT2RY9IB3/e8NyKbNkVaJ4'),
(5, 'jocasta tan', 'jocastatan0171@gmail.com', 'ripthatpuuuuss5', '$5$rounds=535000$9MELO0A7D4IUWPra$ibCU0MB/u/pzgAskaOSbxtIu7IZvN6YhcAYd6hBRQu/');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `stocklist`
--
ALTER TABLE `stocklist`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `stocks`
--
ALTER TABLE `stocks`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `user_flask`
--
ALTER TABLE `user_flask`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `stocklist`
--
ALTER TABLE `stocklist`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `stocks`
--
ALTER TABLE `stocks`
  MODIFY `id` int(8) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3289;

--
-- AUTO_INCREMENT for table `user_flask`
--
ALTER TABLE `user_flask`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
