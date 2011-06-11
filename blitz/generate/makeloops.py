# python version of the makeloops.cpp that generates the benchmark
# loops.

import time, pdb

# definitions of the loops (from loops.data)
loops=[
    ("loop1", ("x","y"),(), ("double", 8), 1, "$x = sqrt($y)"),
    ("loop3", ("x","y"), ("a"), ("double", 8), 2, "$y=$y+$a*$x")
    ]

# handy access functions for readibility
def loopname(loop):
    return loop[0]
def looparrays(loop):
    return loop[1]
def loopscalars(loop):
    return loop[2]
def loopnumtype(loop):
    return loop[3]
def loopflops(loop):
    return loop[4]
def loopexpr(loop):
    return loop[5]

def cc(l):
    return reduce(lambda a,b: a+b, l, "")

def sub_skeleton(skeleton, subs):
    for s in subs:
        skeleton=skeleton.replace("#%s#"%s[0],s[1])
    return skeleton

def fortrandecls(loop):
    arrdecl=cc([", %s* %s"%(loopnumtype(loop)[0], n) for n in looparrays(loop)])
    scaldecl=cc([", const %s& %s"%(loopnumtype(loop)[0], n) for n in loopscalars(loop)])
    decl=cc(["  void %s_%s(const int& N%s%s);\n"%
             (loopname(loop),suffix,arrdecl,scaldecl)
             for suffix in ("f77","f77overhead","f90","f90overhead")])
    return decl

def declandfill(loop, type,datamember):
    decl=cc(["        %s %s(N);\n        initializeRandomDouble(%s.%s(), N);\n"%
             (type, n, n,datamember) for n in looparrays(loop)])
    return decl

def gencpp(loop):
    """Generate the C++ loop code from loop data by substituting the
    skeleton."""
    
    subs=[
        ("loopname",loopname(loop)),
        ("LOOPNAME",loopname(loop).upper()),
        ("gentime",time.asctime(time.gmtime())),
        ("fortrandecls", fortrandecls(loop)),
        ("scalarargdecl", cc([", %s %s"%(loopnumtype(loop)[0], n)
                              for n in loopscalars(loop)])),
        ("scalarargs", cc([", %s"%n for n in loopscalars(loop)])),
        ("loopexpr", loopexpr(loop)),
        ("declarescalars",
         cc(["%s %s = 0.39123982498157938742;\n"%(loopnumtype(loop)[0], n)
             for n in loopscalars(loop)])),
        ("arraydeclandfill",
         declandfill(loop, "Array<%s,1>"%loopnumtype(loop)[0], "dataFirst")),
        ("tvdeclandfill",
         declandfill(loop, "TinyVector<%s,N>"%loopnumtype(loop)[0], "dataFirst")),
        ("looparrayexpr", loopexpr(loop).replace("$",""))
        ]

    cpp =  sub_skeleton(cpp_skeleton, subs)
    f=open("%s.cpp"%loopname(loop),"w")
    f.write(cpp)
    
cpp_skeleton = """


#include <blitz/vector2.h>
#include <blitz/array.h>
#include <blitz/rand-uniform.h>
#include <blitz/benchext.h>

// Generated: makeloops.py #gentime#

#ifdef BZ_HAVE_VALARRAY
 #define BENCHMARK_VALARRAY
#endif

#ifdef BENCHMARK_VALARRAY
#include <valarray>
#endif

BZ_USING_NAMESPACE(blitz)

#if defined(BZ_FORTRAN_SYMBOLS_WITH_TRAILING_UNDERSCORES)
 #define #loopname#_f77 #loopname#_f77_
 #define #loopname#_f77overhead #loopname#_f77overhead_
 #define #loopname#_f90 #loopname#_f90_
 #define #loopname#_f90overhead #loopname#_f90overhead_
#elif defined(BZ_FORTRAN_SYMBOLS_WITH_DOUBLE_TRAILING_UNDERSCORES)
 #define #loopname#_f77 #loopname#_f77__
 #define #loopname#_f77overhead #loopname#_f77overhead__
 #define #loopname#_f90 #loopname#_f90__
 #define #loopname#_f90overhead #loopname#_f90overhead__
#elif defined(BZ_FORTRAN_SYMBOLS_CAPS)
 #define #loopname#_f77 #LOOPNAME#_F77
 #define #loopname#_f77overhead #LOOPNAME#_F77OVERHEAD
 #define #loopname#_f90 #LOOPNAME#_F90
 #define #loopname#_f90overhead #LOOPNAME#_F90OVERHEAD
#endif

extern "C" {
#fortrandecls#
}

void VectorVersion(BenchmarkExt<int>& bench#scalarargdecl#);
void ArrayVersion(BenchmarkExt<int>& bench#scalarargdecl#);
void doTinyVectorVersion(BenchmarkExt<int>& bench#scalarargdecl#);
void F77Version(BenchmarkExt<int>& bench#scalarargdecl#);
#ifdef FORTRAN_90
void F90Version(BenchmarkExt<int>& bench#scalarargdecl#);
#endif
#ifdef BENCHMARK_VALARRAY
void ValarrayVersion(BenchmarkExt<int>& bench#scalarargdecl#);
#endif

extern void sink();

const int numSizes = 20;
const int Nmax=1<<(numSizes-1);
const int tvNmax=7;

int main()
{
    int numBenchmarks = 6;
#ifndef BENCHMARK_VALARRAY
    numBenchmarks--;   // No  valarray
#endif
#ifndef FORTRAN_90
    numBenchmarks--;   // No fortran 90
#endif

    BenchmarkExt<int> bench("#loopname#: #loopexpr#", numBenchmarks);

    bench.setNumParameters(numSizes);
    bench.setRateDescription("Mflops/s");

    Vector<int> parameters(numSizes);
    Vector<long> iters(numSizes);
    Vector<double> flops(numSizes);

    for (int i=0; i < numSizes; ++i)
    {
      parameters(i) = Nmax>>i;
      iters(i) = 50000000L * (parameters(i)<4 ? 4/parameters(i) :1) / parameters(i);
	
        if (iters(i) < 2)
            iters(i) = 2;
        flops(i) = 2 * parameters(i);
    }

    bench.setParameterVector(parameters);
    bench.setIterations(iters);
    bench.setFlopsPerIteration(flops);

    bench.beginBenchmarking();

#declarescalars#

    VectorVersion(bench #scalarargs#);
    ArrayVersion(bench #scalarargs#);
    doTinyVectorVersion(bench #scalarargs#);
    F77Version(bench #scalarargs#);
#ifdef FORTRAN_90
    F90Version(bench #scalarargs#);
#endif
#ifdef BENCHMARK_VALARRAY
    ValarrayVersion(bench #scalarargs#);
#endif

    bench.endBenchmarking();

    bench.saveMatlabGraph("#loopname#.m");
    return 0;
}

template<class T>
void initializeRandomDouble(T data, int numElements, int stride = 1)
{
    static Random<Uniform> rnd;

    for (int i=0; i < numElements; ++i)
        data[size_t(i*stride)] = rnd.random();
}

template<class T>
void initializeArray(T& array, int numElements)
{
    static Random<Uniform> rnd;

    for (size_t i=0; i < numElements; ++i)
        array[i] = rnd.random();
}

void ArrayVersion(BenchmarkExt<int>& bench#scalarargdecl#)
{
    bench.beginImplementation("Array<T,1>");

    while (!bench.doneImplementationBenchmark())
    {
        int N = bench.getParameter();
        cout << "Array<T,1>: N = " << N << endl;

        long iters = bench.getIterations();

#arraydeclandfill#

        bench.start();
        for (long i=0; i < iters; ++i)
        {
	  asm("nop;nop;");
            #looparrayexpr#
	  asm("nop;nop;");
            sink();
        }
        bench.stop();

        bench.startOverhead();
        for (long i=0; i < iters; ++i) {
	  asm("nop;nop;");
            sink();
	  asm("nop;nop;");
	}

        bench.stopOverhead();
    }

    bench.endImplementation();
}
  

template<int N>
void TinyVectorVersion(BenchmarkExt<int>& bench#scalarargdecl#)
{
        cout << "Tinyvector<T, " << N << ">" << endl;
	bench.getParameter();

        long iters = bench.getIterations();

#tvdeclandfill#

        bench.start();
        for (long i=0; i < iters; ++i)
        {
	  asm("nop;nop;");
            #looparrayexpr#
	  asm("nop;nop;");
            sink();
        }
        bench.stop();

        bench.startOverhead();
        for (long i=0; i < iters; ++i) {
	  asm("nop;nop;");
            sink();
	  asm("nop;nop;");
	}
        bench.stopOverhead();

	TinyVectorVersion<N>>1>(bench#scalarargs#);
}

// end recursion
template<>
void TinyVectorVersion<0>(BenchmarkExt<int>& bench#scalarargdecl#)
{}

void doTinyVectorVersion(BenchmarkExt<int>& bench#scalarargdecl#)
{
  bench.beginImplementation("TinyVector<T>");
  // can't run tinyvector with full length because meta-unrolling
  // kills compiler...
  int N=Nmax;
  while(N> 1<<tvNmax) {
   bench.getParameter();
   bench.getIterations();
   bench.skip();
   N>>=1;
  }

  TinyVectorVersion< 1<<tvNmax >(bench,#scalarargs#);
  bench.endImplementation();
}


#ifdef BENCHMARK_VALARRAY
void ValarrayVersion(BenchmarkExt<int>& bench#scalarargdecl#)
{
    bench.beginImplementation("valarray<T>");

    while (!bench.doneImplementationBenchmark())
    {
        int N = bench.getParameter();
        cout << "valarray<T>: N = " << N << endl;

        long iters = bench.getIterations();

        #vararraydeclandfill#

        bench.start();
        for (long i=0; i < iters; ++i)
        {
	  asm("nop;nop;");
            #looparrayexpr#
	  asm("nop;nop;");
            sink();
        }
        bench.stop();

        bench.startOverhead();
        for (long i=0; i < iters; ++i) {
	  asm("nop;nop;");
	  sink();
	  asm("nop;nop;");
	}
        bench.stopOverhead();
    }

    bench.endImplementation();
}
#endif
"""

f77_skeleton = """
      SUBROUTINE #loopname#_F77(N#f77args#)
      INTEGER i, N
      REAL*#numtypesize# #f77decls#

      DO i=1,N
          #f77loopexpr#
      END DO
      RETURN
      END


      SUBROUTINE #loopname#_F77Overhead(N#f77args#)
      INTEGER i, N
      REAL*#numtypesize# #f77decls#
      RETURN
      END
"""

f90_skeleton = """
      SUBROUTINE #loopname#_F90(N, x, y, a)
      INTEGER i, N
      REAL*#numtypesize# #f77decls#

      #f90loopexpr#
      RETURN
      END


      SUBROUTINE #loopname#_F90Overhead(N, x, y, a)
      INTEGER i, N
      REAL*#numtypesize# #f77decls#

      RETURN
      END
"""






    