!                   ************************
                    SUBROUTINE USER_CONDIN_H
!                   ************************
!
!
!***********************************************************************
! TELEMAC2D   V8P4
!***********************************************************************
!
!brief    USER INITIALISES THE PHYSICAL PARAMETERS H
!
!history  J-M HERVOUET (LNHE)
!+        30/08/2007
!+        V6P0
!+
!
!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!
      USE BIEF
      USE DECLARATIONS_TELEMAC
      USE DECLARATIONS_TELEMAC2D
      USE TPXO
      USE OKADA
!
      USE DECLARATIONS_SPECIAL
      IMPLICIT NONE
!
!+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
!
      DOUBLE PRECISION XSOM(4),YSOM(4)
      INTEGER I,NSOM
!
      NSOM = 4
      XSOM(1) =  1999.D0
      XSOM(2) =  3001.D0
      XSOM(3) =  3001.D0
      XSOM(4) =  1999.D0
      YSOM(1) =  40.4D0
      YSOM(2) =  40.4D0
      YSOM(3) =  502.D0
      YSOM(4) =  502.D0
!
      WRITE(LU,11)
11    FORMAT(1X,'CONDIN: WITH SPECIAL INITIAL CONDITIONS'
     &    ,/,1X,'        USER_CONDIN_H MODIFIED' )
!      CALL PLANTE(1)
!      STOP
!
!     POLYGON TO INCLUDE NODES IN THE FLOODPLAIN (2000<x<3000)

      DO I=1,NPOIN
!       CONSTANT FREE SURFACE IN THE FLOODPLAIN
        IF(INPOLY(MESH%X%R(I), MESH%Y%R(I), XSOM, YSOM, NSOM)) THEN
          H%R(I)=6.8D0
          H%R(I)=H%R(I)-ZF%R(I)
        ENDIF
!       CONSTANT DEPTH IN THE CHANNEL (A SORT OF UNIFORM FLOW FOR HOTSTART)
        IF(MESH%Y%R(I).LE.26.D0) THEN
          H%R(I)=-0.0011D0*MESH%X%R(I)+7.6D0
          H%R(I)=H%R(I)-ZF%R(I)
!       ZERO DEPTH OVER THE DYKE
        ELSEIF(MESH%Y%R(I).GT.26.D0.AND.MESH%Y%R(I).LE.42.D0) THEN
          H%R(I)=ZF%R(I)
          H%R(I)=H%R(I)-ZF%R(I)
        ENDIF
      ENDDO
!
!-----------------------------------------------------------------------
!
      RETURN
      END
