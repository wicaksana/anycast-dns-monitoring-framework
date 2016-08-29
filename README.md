# IPv4 vs IPv6 Catchment Areas: a Root DNS Study

## Abstract

Anycast has been extensively used by DNS Root Server operators to improve
performance, resilience, and reliability. In line with the migration 
towards IPv6 networks, 9 out of 11 anycasted Root Servers are running on
both IPv4 and IPv6 (dual-stack mode) today. Ideally, both protocols should
provide similar performances. Problem arises since operators may have 
different peering policies for IPv4 and IPv6 networks, which leads to 
different catchment areas for the same service and potentially different 
quality of service. In this thesis, we analyze the IPv4 and IPv6 
catchments of anycasted Root Servers from control-plane perspective between
February 2008 to June 2016 using BGP data from RIPE RIS. We study the 
evolution and the differences of the catchment areas over the time. We 
also develop visualization tool to help operator assess their catchment 
areas. While we specifically study DNS Root Server, our methodology can be 
applied to other anycast services as well.

## Files

- [Visualization tool](anycast_dns_monitoring/)
- [Scripts to generate graphs](scripts/analysis) 
- [Jupyter notebooks for analysis](scripts/Notebook)
- [database dump (mongodb & neo4j)](db/)


