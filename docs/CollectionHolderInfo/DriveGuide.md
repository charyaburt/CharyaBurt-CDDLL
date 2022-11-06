---
layout: page
title: Hard Drives and Digital Storage
parent: Information for Collection Holders
---

# Hard Drives and Digital Storage

## File Size Estimates

You can estimate size you need if you know the duration of the your tapes and what format you'll be receiving:
* 10-Bit Uncompressed (Preservation) -> 100gb/hr
* Lossless Compressed FFV1 / Matroska (Preservation) -> 40gb/hr
* ProRes 422 HQ (Mezzanine) -> 30gb/hr
* H.264 / MP4  (Access) -> 1gb/hr

If you'd like a more accurate estimate you can reach out to us and we will create one for you.

Once you have your size estimate, make sure you that you won't fill your hard drive above 85% capacity.

## Buying a Hard Drives

Once you know how much space you'll need you can buy a drive. There's a number of different types of drives you can buy. The following is a discussion of these different types.

### Flash Drives

Flash drives are an excellent and cost effective option for moving files between computers. However, they are ***NOT*** a good option for longterm storage. As the capacity of these drives continues to increase they're quickly becoming a viable option for handling the transmission large preservation-grade files. However, do not expect to use a flash drive for storing your collection, as they have a very high rate of failure.

### Portable External Hard Drives

Portable drives are small and often powered by the USB or Thunderbolt cable that is plugged into them. These are more reliable than Flash Drives, small, light, and easy to ship. We recommend against using these drives for long-term storage because these small, bus-powered enclosures are not quite as robust as full-sized external drives. However, a portable external drive would make an excellent and cost-effective second or third backup copy.

### Full-Sized External Hard Drives

Full-sized drives are often desktop units that plug into a wall and have  one or more USB or Thunderbolt connections in the back. These are often more robust than portable drives, especially if you buy from a high-quality brand or vendor (see below). These drives are great for long-term storage as long as you have multiple copies stored across multiple drives.

### RAID Drives

RAID stands for "Redundant Array of Inexpensive Disks" or "Redundant Array of Independent Disks". This is a setup in which one or more disks are connected in such a way that the computer sees them as one single volume. There are a number of different RAID configurations. We won't go into a ton of detail describing them, but you can look them up if you look. It's important to note that even for RAID configurations that have redundancy or parity, you still need to have a copy of the files on a another drive in case your entire RAID array fails.

**RAID 0:** The data is written across multiple drives for faster read access. This is excellent for video editing, but awful for preservation. If you lost one drive you lose all the data.

**RAID 1:** The data is mirrored across every drive. This is great for preservation but can very slow to write to.

**RAID 5:** The data is written across many drives, and also redundant. You need at least three discs to use RAID 5, and you can lose one drive without losing any data. This is good for preservation but is still geared more towards production.

**RAID 6:** The data is written across many drives, and also redundant. You need at least four discs to use RAID 6, and you can lose two drives without losing any data. This is good for preservation, better than RAID 5 even, but is expensive (you need many drives) and is still geared more towards production.

**RAID 10:** This is mix of RAID 1 and RAID 0. The discs are mirrored and also striped. This is good for preservation but requires many drives and is slow.

### Bare Hard Drives

Another option for storage is to purchase drives that have no enclosure. These are drives that you would typically put inside of a computer or a RAID array. This isn't a common approach because you need a different set of equipment to access the data on a bare drive, and because the drives themselves are more fragile without an enclosure. However, adding an enclosure does add an extra point of failure, so having a drive without an enclosure minimizes the potential points of failure.

If you choose to go this route you should buy cases for your drives, and a [drive dock](https://eshop.macsales.com/item/OWC/TCDRVDCK). Make sure you keep the drive in a case when it's not being used because the connections are fragile!

### Cloud storage

Cloud storage is quickly becoming cheaper and more widely available. However, the preservation files we create are very large, and it can be dificult or expensive to upload files of this size to most cloud services unless you have a professional-grade internet provider.

If you chose to use cloud storage, you should consider keeping a copy of the files locally on a drive as well. While most cloud storage vendors will likely be around for a while, companies can go bankrupt and disappear overnight.

### Hard Disk Drive (HDD) vs Solid State Drive (SSD)

As SSD drives become cheaper with larger capacity, they are becoming an attractive option for archiving and preservation. HDD drives can be fragile, as the platters can break if dropped. SSD drives are far more robust, since they have no moving parts. Early studies suggested that SSD drives can burn themselves out if they are written to many times, making them a poor choice for video editing or production. However, this doens't pose an issue in an archival context, when the drives are written to once and then only read from then on out.

Overally it seems that many of the concerns about the longevity of SSD drives may have been fixed with advanced technology. Still, HDDs have proven to be robust and long-lasting, while the jury is still out on SSDs. At BAVC we have experience using both, and haven't noticed any issues that occur more with SSDs or with HDDs.

### Which Brand To Buy?

The following brands are excellent and make high quality drives.
- G-Drive
- LaCie
- Fantom
- OWC
- HGST

The following companies make consumer and budget=grade drives that are fine, but not as sturdy as the previously mentioned companies
- Western Digital
- Seagate
- Toshiba
- SanDisc

Do not buy a drive from a manufacturer that you do not recognize, or do not trust.

## Maintaining Files on Hard Drives

It is very important to note that you should always have at least two copies of any file you want preserved on at least two different drives. Even if you purchase the best and most expensive drive available on the market, there is still a chance that the drive can fail. If your only copy of a file exists on a faild drive then the file will be lost. If yor budget is low, consider buying multiple cheap drives. Even if these drives have a higher failure rate, keeping multiple copies on multiple drives is the only way to truly ensure the longterm preservation of digital files.

Hard drives tend to have a life-span of about five years. This isn't set in stone, but it is a good idea to migrate your files to a new drive every five years or so to be safe.

The best way to make sure the files on your drive are safe is to run regular [fixity checks](https://www.dpconline.org/handbook/technical-solutions-and-tools/fixity-and-checksums). There are many resources available online for running fixity checks. The process can be difficult for the technically uninclined, but if you want to make sure your files are safe and secure you should consider reading the linked article and having a fixity plan.
