!                   *******************************
                    SUBROUTINE USER_UTIMP_TELEMAC2D
!                   *******************************
!
     &(LTL,ATL,GRADEBL,GRAPRDL,LISDEBL,LISPRDL)
!
!***********************************************************************
! TELEMAC2D
!***********************************************************************
!
!brief    WRITES OUT ADDITIONAL OUTPUT REQUIRED BY THE USER.
!
!note     THIS SUBROUTINE IS CALLED IN THE SAME PLACES AS THE
!+                MAIN TELEMAC2D OUTPUT SUBROUTINE (NAMED DESIMP),
!+                I.E. CALLED TWICE:
!+
!note   (1) ONCE PER RUN, WHEN LTL==0, INDEPENDENTLY OF WHETHER
!+             'OUTPUT OF INITIAL CONDITIONS : YES' IS SET OR NOT
!note   (2) EACH TIME STEP JUST AFTER DESIMP-OUTPUT
!
!history  JACEK A. JANKOWSKI PINXIT, BAW KARLSRUHE, JACEK.JANKOWSKI@BAW.DE
!+        **/08/2003
!+        V5P4
!+
!
!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!| ATL            |-->| TIME OF TIME STEP, IN SECONDS
!| GRADEBL        |-->| FIRST TIME STEP FOR GRAPHIC OUTPUTS
!| GRAPRDL        |-->| PERIOD OF GRAPHIC OUTPUTS
!| LISDEBL        |-->| FIRST TIME STEP FOR LISTING OUTPUTS
!| LISPRDL        |-->| PERIOD OF LISTING OUTPUTS
!| LTL            |-->| CURRENT TIME STEP
!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!
      USE BIEF
      USE DECLARATIONS_TELEMAC
      USE DECLARATIONS_TELEMAC2D
!
      USE DECLARATIONS_SPECIAL
      USE INTERFACE_PARALLEL, ONLY : P_MAX
      IMPLICIT NONE
!
!+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
!
      DOUBLE PRECISION, INTENT(IN) :: ATL
      INTEGER, INTENT(IN) :: LTL,GRADEBL,GRAPRDL,LISDEBL,LISPRDL
!
!+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
!
      INTEGER FID
      DOUBLE PRECISION FS_BR1,FS_BR2,VEL,HEADRIV,HEADFLP,DEUXG,DELTAHEAD
!
!-----------------------------------------------------------------------
!
      DEUXG = 2.D0*GRAV
!
!     FREE SURFACE AND DIFFERENCE OF HYDRAULIC LOAD FOR BREACH 1 :
!     NODES 13352,13352,13400
!     FREE SURFACE FOR BREACH 2 :
!     NODES 9406
      FS_BR1=H%R(NUMPSD%I(1))+ZF%R(NUMPSD%I(1))
      FS_BR2=H%R(NUMPSD%I(2))+ZF%R(NUMPSD%I(2))
!     CASE WHERE WE ARE BETWEEN SEVERAL SUB-DOMAINS ??
!     HYDRAULIC HEAD
      VEL=U%R(NUMRIV%I(1))**2+V%R(NUMRIV%I(1))**2
      HEADRIV = ZF%R(NUMRIV%I(1)) + H%R(NUMRIV%I(1)) + VEL/DEUXG
      VEL=U%R(NUMFLP%I(1))**2+V%R(NUMFLP%I(1))**2
      HEADFLP = ZF%R(NUMFLP%I(1)) + H%R(NUMFLP%I(1)) + VEL/DEUXG
!     CASE WHERE WE ARE BETWEEN SEVERAL SUB-DOMAINS
      IF(NCSIZE.GT.1) THEN
        HEADRIV = P_MAX(HEADRIV)
        HEADFLP = P_MAX(HEADFLP)
      ENDIF
      DELTAHEAD=ABS(HEADRIV-HEADFLP)
!
!     IF PARALLEL ONLY WRITE WITH FIRST NODE
      IF(IPID.EQ.0) THEN
        FID = T2D_FILES(T2DRFO)%LU
        WRITE(FID,1001) AT,FS_BR1,FS_BR2,DELTAHEAD
      ENDIF
!
 1001 FORMAT((F10.4,1X,F10.4,1X,F10.4,1X,F10.4))
!-----------------------------------------------------------------------
!
      RETURN
      END SUBROUTINE
