DROP TABLE IF EXISTS `ad_ctr`;
CREATE TABLE `ad_ctr` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `code` varchar(64) DEFAULT NULL COMMENT '广告编号',
    `show_count` int(11)  DEFAULT NULL COMMENT '全天总曝光量',
    `click_count` int(11)  DEFAULT NULL COMMENT '全天总点击量',
    `crt` float(4,2) DEFAULT NULL COMMENT '全天点击率',
    `show_day` varchar(300) DEFAULT NULL COMMENT '全天时段曝光量',
    `click_day` varchar(300) DEFAULT NULL COMMENT '全天时段点击量',
    `note` varchar(32) DEFAULT NULL,
    `create_date`  timestamp NULL DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '统计日期',
    `create_time` timestamp NULL DEFAULT NULL,
    `update_time` timestamp NULL DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;
 

DROP TABLE IF EXISTS `ad_style`;
CREATE TABLE `ad_style` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `code` varchar(64) DEFAULT NULL COMMENT '广告编号',
    `group_id` int(11)  DEFAULT NULL COMMENT '分组id :ad_group.id',
    `image_id` int(11)  DEFAULT NULL COMMENT '图片id ->ad_image.id',
    `oper_uid` int(11)  DEFAULT NULL COMMENT '操作人id;user.id',
    `oper_uname` varchar(11) DEFAULT NULL COMMENT '操作人username',
    `status` int(11)  DEFAULT 2 COMMENT '状态(0：已下架 1：已上架 2:暂存未发布 3:已删除弃用)',
    `close` int(11)  DEFAULT 0 COMMENT '是否可点击关闭(0：可关闭；1：不可关闭 )',
    `mode` int(11)  DEFAULT 0 COMMENT '图片展示方式: 轮播,横幅',
    `frequency` varchar(5) DEFAULT "0.5" COMMENT '图片轮播的频率0.1-0.5s',    
    `position` varchar(5) DEFAULT 1 COMMENT '图片摆放位置: 1:首页banner,2:首页底部,3:商场banner',  
    `system` int(11) DEFAULT 1 COMMENT '1:运营后台, 2:XX端注册, 3:DD端',  
    `note` varchar(32) DEFAULT NULL,
    `up_time` timestamp NULL DEFAULT NULL COMMENT '上架时间',
    `down_time` timestamp NULL DEFAULT NULL COMMENT '下架时间',
    `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '创建时间',
    `update_time` timestamp NULL DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `ad_image`;
CREATE TABLE `ad_image` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `group_id` int(11)  DEFAULT NULL COMMENT '分组id :ad_group.id',
    `image_name` varchar(124) DEFAULT NULL COMMENT '图片名',
    `image_url` varchar(124) DEFAULT NULL COMMENT '图片存放链接',
    `note` varchar(32) DEFAULT NULL,
    `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '创建时间',
    `update_time` timestamp NULL DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `ad_group`;
CREATE TABLE `ad_group` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `name` varchar(64) NOT NULL COMMENT '组名',
    `note` varchar(32) DEFAULT NULL,
    `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '创建时间',
    `update_time` timestamp NULL DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `unique_group` (`group`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

