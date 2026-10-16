![openTELEMAC][telemac-banner]

Introduction
============

The TELEMAC system is an integrated suite of solvers used in the fields of
free-surface flow, wave propagation and sediment transport. Having been used in
the context of numerous studies throughout the world and the subject of several
peer-reviewed publications, it has become one of the major standards in its
field.

The TELEMAC system is managed by a consortium of organisations: Artelia
(France), BundesAnstalt für Wasserbau (BAW, Germany), Centre d'études et
d'expertise sur les risques, l'environnement, la mobilité et l'aménagement
(CEREMA, France), Électricité de France (EDF, France), HR Wallingford (United
Kingdom) and International Marine and Dredging Consultants (IMDC, Belgium). It
is further strengthened scientifically by Daresbury Laboratory (United
Kingdom), the Centre Européen de Recherche et de Formation Avancée en Calcul
Scientifique (CERFACS, France) and the École des Ponts ParisTech (France).

The TELEMAC system is used by most engineers for dimensioning and
impact studies, where safety is prevailing and, for this reason, reliability,
validation and a worldwide recognition of our tools are of utmost importance.
As a consequence and to improve the access to TELEMAC for the whole community
of consultants and researchers, the choice of open source has been made. Anyone
can thus take advantage of the TELEMAC system and assess its performances and
will find necessary resources on the official website. Besides, the quality of 
assistance, maintenance and hotline support are also very important to 
professional users, and a special effort has been made to offer alternatively a
broad range of fee-paying services.

Learning Resources
==================

* General information is available at
[TELEMAC official website](http://www.opentelemac.org).

* Community discussion takes place on the
[TELEMAC forum](https://opentelemac.org/index.php/kunena) (registration
required).

* A set of guides dedicated to each of the TELEMAC system modules is generated
in PDF format for each new major release.

* There is also a large collection of [TELEMAC Examples](./examples/) showing 
different use cases for each of the system modules, providing a useful learning
resource.

Building
========

The TELEMAC system is written in Fortran 90 and uses a subset of the features
provided by the Fortran 2003 standard. As a result, any recent Fortran compiler
should be able to compile the different modules of the system.

Additionnaly, TELEMAC building, execution and validation depend on a set of
Python scripts. All versions of Python that have not reached end-of-life are
supported by the system. This means that the minimum version of Python that is
currently supported is 3.8.

TELEMAC is built and tested at EDF on a nightly basis, using the following
compilers and versions of Python:

* Debian 10: GFortran 8.3.0, Python 3.8.18
* Debian 11: GFortran 10.2.1, Python 3.9.17
* RHEL 8.3: GFortran 8.4.1, Python 3.8.18

**Windows** users can look at the
[wintel](https://gitlab.pam-retd.fr/otm/wintel) Git Repository, which provides
all the necessary information to build TELEMAC on Windows using MinGW-w64.

**Linux** users can find information on how to build TELEMAC on their
distribution on the
[TELEMAC Wiki](http://wiki.opentelemac.org/doku.php?id=installation_notes_2_beta)

[telemac-banner]: telemac-banner.png


License
=======

The TELEMAC system is distributed under the GNU General Public License v3.0
(GPLv3). See [LICENSE.txt](./LICENSE.txt) for details.
