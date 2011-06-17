
// floop3 generated by makeloops.py Fri Jun 17 15:34:51 2011

#include <blitz/vector2.h>
#include <blitz/array.h>
#include <random/uniform.h>
#include <blitz/benchext.h>

#ifdef BZ_HAVE_VALARRAY
 #define BENCHMARK_VALARRAY
#endif

#ifdef BENCHMARK_VALARRAY
#include <valarray>
#endif

BZ_NAMESPACE(blitz)
extern void sink();
BZ_NAMESPACE_END

BZ_USING_NAMESPACE(blitz)
BZ_USING_NAMESPACE(std)

#if defined(BZ_FORTRAN_SYMBOLS_WITH_TRAILING_UNDERSCORES)
 #define floop3_f77 floop3_f77_
 #define floop3_f77overhead floop3_f77overhead_
 #define floop3_f90 floop3_f90_
 #define floop3_f90overhead floop3_f90overhead_
#elif defined(BZ_FORTRAN_SYMBOLS_WITH_DOUBLE_TRAILING_UNDERSCORES)
 #define floop3_f77 floop3_f77__
 #define floop3_f77overhead floop3_f77overhead__
 #define floop3_f90 floop3_f90__
 #define floop3_f90overhead floop3_f90overhead__
#elif defined(BZ_FORTRAN_SYMBOLS_CAPS)
 #define floop3_f77 FLOOP3_F77
 #define floop3_f77overhead FLOOP3_F77OVERHEAD
 #define floop3_f90 FLOOP3_F90
 #define floop3_f90overhead FLOOP3_F90OVERHEAD
#endif

extern "C" {
  void floop3_f77(const int& N, float* x, float* y, const float& a);
  void floop3_f77overhead(const int& N, float* x, float* y, const float& a);
  void floop3_f90(const int& N, float* x, float* y, const float& a);
  void floop3_f90overhead(const int& N, float* x, float* y, const float& a);

}

void VectorVersion(BenchmarkExt<int>& bench, float a);
void ArrayVersion(BenchmarkExt<int>& bench, float a);
void doTinyVectorVersion(BenchmarkExt<int>& bench, float a);
void F77Version(BenchmarkExt<int>& bench, float a);
#ifdef FORTRAN_90
void F90Version(BenchmarkExt<int>& bench, float a);
#endif
#ifdef BENCHMARK_VALARRAY
void ValarrayVersion(BenchmarkExt<int>& bench, float a);
#endif

const int numSizes = 20;
const int Nmax=1<<(numSizes-1);
const int tvNmax=7;
const bool runvector=true;

int main()
{
    int numBenchmarks = runvector ? 6 : 5;
#ifndef BENCHMARK_VALARRAY
    numBenchmarks--;   // No  valarray
#endif
#ifndef FORTRAN_90
    numBenchmarks--;   // No fortran 90
#endif

    BenchmarkExt<int> bench("floop3: $y = $y + a*$x", numBenchmarks);

    bench.setNumParameters(numSizes);

    Array<int,1> parameters(numSizes);
    Array<long,1> iters(numSizes);
    Array<double,1> flops(numSizes);

    for (int i=0; i < numSizes; ++i)
    {
      parameters(i) = Nmax>>i;
      iters(i) = 50000000L / parameters(i);
	
        if (iters(i) < 2)
            iters(i) = 2;
        flops(i) = 2 * parameters(i);
    }

    bench.setParameterVector(parameters);
    bench.setIterations(iters);
    bench.setFlopsPerIteration(flops);

    bench.beginBenchmarking();

float a = 0.39123982498157938742;


    ArrayVersion(bench , a);
    doTinyVectorVersion(bench , a);
    F77Version(bench , a);
#ifdef FORTRAN_90
    F90Version(bench , a);
#endif
#ifdef BENCHMARK_VALARRAY
    ValarrayVersion(bench , a);
#endif

    if(runvector)
      VectorVersion(bench , a);

    bench.endBenchmarking();

    bench.saveMatlabGraph("floop3.m");
    return 0;
}

template<class T>
void initializeRandomDouble(T* data, int numElements, int stride = 1)
{
    ranlib::Uniform<T> rnd;

    for (int i=0; i < numElements; ++i)
        data[size_t(i*stride)] = rnd.random();
}

template<class T>
void initializeRandomDouble(valarray<T>& data, int numElements, int stride = 1)
{
    ranlib::Uniform<T> rnd;

    for (int i=0; i < numElements; ++i)
        data[size_t(i*stride)] = rnd.random();
}

void VectorVersion(BenchmarkExt<int>& bench, float a)
{
    bench.beginImplementation("Vector<T>");

    while (!bench.doneImplementationBenchmark())
    {
        int N = bench.getParameter();
        long iters = bench.getIterations();

        cout << "Vector<T>: N = " << N << endl;

        Vector<float> x(N);
        initializeRandomDouble(x.data(), N);
        Vector<float> y(N);
        initializeRandomDouble(y.data(), N);


        bench.start();
        for (long i=0; i < iters; ++i)
        {
            y = y + a*x;
            sink();
        }
        bench.stop();

        bench.startOverhead();
        for (long i=0; i < iters; ++i) {
            sink();
	}

        bench.stopOverhead();
    }

    bench.endImplementation();
}


  void ArrayVersion(BenchmarkExt<int>& bench, float a)
{
    bench.beginImplementation("Array<T,1>");

    while (!bench.doneImplementationBenchmark())
    {
        int N = bench.getParameter();
        long iters = bench.getIterations();

        cout << "Array<T,1>: N = " << N << endl;

        Array<float,1> x(N);
        initializeRandomDouble(x.dataFirst(), N);
        Array<float,1> y(N);
        initializeRandomDouble(y.dataFirst(), N);


        bench.start();
        for (long i=0; i < iters; ++i)
        {
            y = y + a*x;
            sink();
        }
        bench.stop();

        bench.startOverhead();
        for (long i=0; i < iters; ++i) {
            sink();
	}

        bench.stopOverhead();
    }

    bench.endImplementation();
}


template<int N>
void TinyVectorVersion(BenchmarkExt<int>& bench, float a)
{
        cout << "Tinyvector<T, " << N << ">" << endl;
        const int sz = bench.getParameter();
        assert(N==sz);
                           
        long iters = bench.getIterations();

        TinyVector<float,N> x(N);
        initializeRandomDouble(x.dataFirst(), N);
        TinyVector<float,N> y(N);
        initializeRandomDouble(y.dataFirst(), N);


        bench.start();
        for (long i=0; i < iters; ++i)
        {
            y = y + a*x;
            sink();
        }
        bench.stop();

        bench.startOverhead();
        for (long i=0; i < iters; ++i) {
            sink();
	}
        bench.stopOverhead();

	TinyVectorVersion<N>>1>(bench, a);
}

// end recursion
template<>
void TinyVectorVersion<0>(BenchmarkExt<int>& bench, float a)
{}

void doTinyVectorVersion(BenchmarkExt<int>& bench, float a)
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

  TinyVectorVersion< 1<<tvNmax >(bench, a);
  bench.endImplementation();
}


#ifdef BENCHMARK_VALARRAY
void ValarrayVersion(BenchmarkExt<int>& bench, float a)
{
    bench.beginImplementation("valarray<T>");

    while (!bench.doneImplementationBenchmark())
    {
        int N = bench.getParameter();
        cout << "valarray<T>: N = " << N << endl;

        long iters = bench.getIterations();

        valarray<float> x(N);
        initializeRandomDouble(x, N);
        valarray<float> y(N);
        initializeRandomDouble(y, N);


        bench.start();
        for (long i=0; i < iters; ++i)
        {
            y = y + a*x;
            sink();
        }
        bench.stop();

        bench.startOverhead();
        for (long i=0; i < iters; ++i) {
	  sink();
	}
        bench.stopOverhead();
    }

    bench.endImplementation();
}
#endif

void F77Version(BenchmarkExt<int>& bench, float a)
{
    bench.beginImplementation("Fortran 77");

    while (!bench.doneImplementationBenchmark())
    {
        int N = bench.getParameter();
        cout << "Fortran 77: N = " << N << endl;

        int iters = bench.getIterations();

        float* x = new float[N];
        initializeRandomDouble(x, N);
        float* y = new float[N];
        initializeRandomDouble(y, N);
        

        bench.start();
        for (int iter=0; iter < iters; ++iter)
            floop3_f77(N, x, y, a);
        bench.stop();

        bench.startOverhead();
        for (int iter=0; iter < iters; ++iter)
            floop3_f77overhead(N, x, y, a);

        bench.stopOverhead();

        delete [] x;
        delete [] y;

    }

    bench.endImplementation();
}

#ifdef FORTRAN_90
void F90Version(BenchmarkExt<int>& bench, float a)
{
    bench.beginImplementation("Fortran 90");

    while (!bench.doneImplementationBenchmark())
    {
        int N = bench.getParameter();
        cout << "Fortran 90: N = " << N << endl;

        int iters = bench.getIterations();

        float* x = new float[N];
        initializeRandomDouble(x, N);
        float* y = new float[N];
        initializeRandomDouble(y, N);


        bench.start();
        for (int iter=0; iter < iters; ++iter)
            floop3_f90(N, x, y, a);
        bench.stop();

        bench.startOverhead();
        for (int iter=0; iter < iters; ++iter)
            floop3_f90overhead(N, x, y, a);

        bench.stopOverhead();
        delete [] x;
        delete [] y;

    }

    bench.endImplementation();
}
#endif

