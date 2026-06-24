using System;
using taste_vnv_toolkit.Models;
using Xunit;

namespace taste_vnv_toolkit_tests;

/// <summary>
/// Initialises Python once before any Python test runs and shuts it down
/// after the last one.  Shared across all classes in "PythonTests".
/// </summary>
public sealed class PythonFixture : IDisposable
{
    public PythonFixture() => PythonRunner.Initialize();
    public void Dispose() => PythonRunner.Shutdown();
}

/// <summary>
/// Collection definition that ties Python test classes to the shared
/// <see cref="PythonFixture"/>.  All classes marked with
/// [Collection("PythonTests")] share one fixture instance and run
/// sequentially (no parallel Python use).
/// </summary>
[CollectionDefinition("PythonTests", DisableParallelization = true)]
public class PythonTestsCollection : ICollectionFixture<PythonFixture> { }
